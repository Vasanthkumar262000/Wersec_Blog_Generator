from dotenv import load_dotenv
from pydamic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_anthropic import Anthropic


load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
llm_anthropic = Anthropic(model="claude-2", temperature=0.7)

