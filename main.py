from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent


load_dotenv()

class BlogPostResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

parser = PydanticOutputParser(pydantic_object=BlogPostResponse)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that generates blog post summaries."
    "Given a topic, you will provide a summary, list of sources, and tools used to generate the content."
    "The provided information should be accurate and relevant to the topic."
    "Blog has to be in markdown format."
    "Wrap the output in this format and provide no other text\n{format_instructions}"),
    ("placeholder", "{messages}"),
]).partial(format_instructions=parser.get_format_instructions())

agent = create_react_agent(
    model=llm,
    prompt=prompt,
    tools=[]
)

raw_response = agent.invoke({"messages": [{"role": "user", "content": "The impact of AI on cybersecurity in 2024"}]})

print(raw_response)



try:
    structured_response = parser.parse(raw_response["messages"][-1].content)
except Exception as e:
    print(f"Error parsing response:",e ," Raw response:" , raw_response)