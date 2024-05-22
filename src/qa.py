import argparse

from langchain_community.llms import Ollama
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class QA:
    def __init__(self, args):
        self.args = args
        self.llm = Ollama(model="llama3", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

    def _ask_rag(self, query: str) -> None:
        model_name = "all-MiniLM-L6-v2.gguf2.f16.gguf"
        gpt4all_kwargs = {'allow_download': 'True'}
        embeddings = GPT4AllEmbeddings(
            model_name=model_name,
            gpt4all_kwargs=gpt4all_kwargs
        )
        persist_dir = 'db'
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        {context}
        Question: {question}
        Helpful Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )

        # Retrieves the appropriate context from the vector DB:
        qa_chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        )
        qa_chain.invoke({"query": query})

    def _ask_non_rag(self, query: str) -> None: 
        template = f"""nswer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        Question: {query}
        Helpful Answer:"""
        self.llm.invoke(template)
