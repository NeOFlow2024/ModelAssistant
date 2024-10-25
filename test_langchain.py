import os
import openai


openai.api_key  = os.environ['OPENAI_API_KEY']

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(r"C:\Users\Abhim\OneDrive\Documents\OpenAI\documents\black_scholes73.pdf")
pages = loader.load()

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter


chunk_size = 64
chunk_overlap = 16

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)
texts = r_splitter.split_text(pages[0].page_content)
#for t in texts:
#    print(f">>({len(t)}){t}")

from langchain.text_splitter import TokenTextSplitter
text_splitter = TokenTextSplitter(chunk_size=128, chunk_overlap=8)
texts = text_splitter.split_text(pages[3].page_content)
#for t in texts:
#    print(f">>({len(t)}){t}")

from langchain_openai import OpenAIEmbeddings
embedding = OpenAIEmbeddings()

a = embedding.embed_query("Testing if embedding works")
b = embedding.embed_query("Hello world")

import numpy as np
np.dot(a, b)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1500,
    chunk_overlap = 150
)
splits = text_splitter.split_documents(pages)

from langchain_community.vectorstores import Chroma

persist_directory = r'C:\Users\Abhim\OneDrive\Documents\OpenAI\chroma\bs'

# Automatically persisted
vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=persist_directory
)
res = vectordb._collection.count()

question = "how does volatility affect option price"

docs = vectordb.similarity_search(question,k=3)

docs2 = vectordb.max_marginal_relevance_search(question, k=2, fetch_k=3)


from langchain_openai import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

metadata_field_info = [
    AttributeInfo(
        name="section",
        description="The section heading",
        type="string",
    ),
]


document_content_description = "Back Scholes option pricing paper"
llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm,
    vectordb,
    document_content_description,
    metadata_field_info,
    verbose=True
)
docs3 = retriever.invoke(question)

llm_name = "gpt-3.5-turbo"

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name=llm_name, temperature=0)

from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever()
)

result = qa_chain.invoke({"query":
"""
Give the source of document used to answer this question.
How does volatility affect option price?
"""
})
result = qa_chain.invoke({"query":
"""
Answer using content in C:\\Users\\Abhim\\OneDrive\\Documents\\OpenAI\\documents\\black_scholes73.pdf and give the page number
How does volatility affect option price?
"""
})
