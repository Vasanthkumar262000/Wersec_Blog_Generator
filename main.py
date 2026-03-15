import re
import time
import pathlib
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from search_tools import search_tool

load_dotenv()


class BlogPostResponse(BaseModel):
    topic: str
    summary: str
    full_content: str
    sources: list[str]
    tools_used: list[str]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _make_llm() -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)


def _research(topic: str, llm: ChatGroq, retries: int = 2) -> str:
    """Run research agent with retry. Returns research text or fallback."""
    agent = create_react_agent(model=llm, tools=[search_tool])
    for attempt in range(retries):
        try:
            result = agent.invoke({"messages": [
                {"role": "user", "content": (
                    f"Research this cybersecurity topic: {topic}. "
                    "Use DuckDuckGo to find recent news, statistics, and key facts. "
                    "Summarize what you find."
                )}
            ]})
            return result["messages"][-1].content
        except Exception as e:
            err = str(e)
            if "403" in err or "429" in err or "rate" in err.lower():
                wait = 5 * (attempt + 1)
                print(f"Groq rate limit / access error (attempt {attempt+1}). Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"Research failed: {e}")
                break
    return f"General knowledge about: {topic}"


def _write_blog(topic: str, tone: str, word_count: str, research: str, llm: ChatGroq, retries: int = 3) -> BlogPostResponse:
    """Write structured blog with retry on rate limits."""
    writer = llm.with_structured_output(BlogPostResponse)
    system = (
        f"You are a cybersecurity content writer for the Wersec team. "
        f"Write a LinkedIn blog post. Tone: {tone}. Length: {word_count}. "
        "Write the full blog post in markdown in the full_content field. "
        "Summary must be 2-3 sentences. List actual sources. List tools used."
    )
    human = f"Topic: {topic}\n\nResearch:\n{research}"

    for attempt in range(retries):
        try:
            return writer.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        except Exception as e:
            err = str(e)
            if "403" in err or "429" in err or "rate" in err.lower():
                wait = 10 * (attempt + 1)
                print(f"Groq rate limit / access error (attempt {attempt+1}). Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(
        "Groq API returned 403 Access Denied after retries. "
        "This is usually caused by:\n"
        "  1. VPN or firewall blocking Groq\n"
        "  2. Groq rate limit — wait a minute and try again\n"
        "  3. Check status.groq.com"
    )


def generate_blog(topic: str, tone: str = "professional", length: str = "medium") -> BlogPostResponse:
    length_map = {
        "short": "300-500 words",
        "medium": "600-900 words",
        "long": "1000-1400 words",
    }
    word_count = length_map.get(length.lower(), "600-900 words")
    llm = _make_llm()

    research = _research(topic, llm)
    result = _write_blog(topic, tone, word_count, research, llm)

    pathlib.Path("outputs").mkdir(exist_ok=True)
    filepath = pathlib.Path("outputs") / f"{_slug(result.topic)}.md"
    filepath.write_text(result.full_content, encoding="utf-8")

    return result


if __name__ == "__main__":
    query = input("Enter a topic for the blog post: ")
    tone = input("Tone (professional/casual/technical) [professional]: ").strip() or "professional"
    length = input("Length (short/medium/long) [medium]: ").strip() or "medium"
    result = generate_blog(query, tone, length)
    print("\n--- Generated Blog ---")
    print(result.full_content)
    print("\n--- Sources ---")
    for s in result.sources:
        print(f"  - {s}")
