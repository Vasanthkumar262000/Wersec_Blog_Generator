import re
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


def generate_blog(topic: str, tone: str = "professional", length: str = "medium") -> BlogPostResponse:
    length_map = {
        "short": "300-500 words",
        "medium": "600-900 words",
        "long": "1000-1400 words",
    }
    word_count = length_map.get(length.lower(), "600-900 words")

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

    # Step 1: Research agent — searches the web and returns findings
    research_agent = create_react_agent(model=llm, tools=[search_tool])
    research_result = research_agent.invoke({"messages": [
        {"role": "user", "content": (
            f"Research this cybersecurity topic thoroughly: {topic}. "
            "Use DuckDuckGo to find recent news, statistics, expert opinions, and key facts. "
            "Summarize everything you find in detail."
        )}
    ]})
    research_content = research_result["messages"][-1].content

    # Step 2: Structured writer — uses research to write the blog post
    writer_llm = llm.with_structured_output(BlogPostResponse)
    result = writer_llm.invoke([
        SystemMessage(content=(
            f"You are a cybersecurity content writer for the Wersec team. "
            f"Write a LinkedIn blog post with tone: {tone}, length: {word_count}. "
            "Use the research provided to write an accurate and engaging post. "
            "The full_content field must contain the complete blog post in markdown format. "
            "The summary field must be 2-3 sentences. "
            "List the actual sources found during research. "
            "List the tools used during research."
        )),
        HumanMessage(content=(
            f"Topic: {topic}\n\n"
            f"Research findings:\n{research_content}"
        )),
    ])

    # Save blog as markdown file
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
