from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor


load_dotenv()

class BlogPostResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
llm_anthropic = ChatAnthropic(model="claude-2", temperature=0.7)

parser = PydanticOutputParser(pydantic_object=BlogPostResponse)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that generates blog post summaries."
    "Given a topic, you will provide a summary, list of sources, and tools used to generate the content."
    "The provided information should be accurate and relevant to the topic."
    "Blog has to be in markdown format."
    "Wrap the output in this format and provide no other text\n{format_instructions}"),
    ("human", "{topic}"),
    ("placeholder","{chat_history}"),
    ("placeholder","{agent_scratchpad}")
]).partial_format(format_instructions=parser.get_format_instructions())


agent = create_tool_calling_agent(
    llm = llm, 
    tools = [], 
    prompt = prompt)

agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
raw_response = agent_executor.invoke({"topic": "The impact of AI on cybersecurity in 2024"})

print(raw_response)

