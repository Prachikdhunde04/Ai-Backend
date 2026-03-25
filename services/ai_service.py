import os
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings

# Initialize Models
llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.LLM_MODEL)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store():
    # Instantiate Vector Store lazily
    return Chroma(
        collection_name="company_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

def add_document_to_rag(texts, metadatas):
    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas)

def query_rag(question: str):
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_template(
        """You are a secure internal company AI assistant. Use the provided context to answer the user's question. 
        Do not make up facts. If you don't know the answer based on the context, state that clearly.
        
        Context: {context}
        
        Question: {input}
        
        Answer:"""
    )
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)

def summarize_text(text: str):
    prompt = ChatPromptTemplate.from_template(
        "Please provide a concise summary of the following document and list the key points:\n\n{text}"
    )
    chain = prompt | llm
    return chain.invoke({"text": text})
