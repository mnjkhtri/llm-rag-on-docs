import glob
import os
from typing import List, Set
from multiprocessing import Pool
from tqdm import tqdm

from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
    UnstructuredMarkdownLoader,
)

from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentLoader:
    def __init__(self, parent_dir = "source_files"):
        self.parent_dir = parent_dir

        self.ext_to_loader = {
            ".txt": (TextLoader, {"encoding": "utf8"}),
            ".pdf": (PyMuPDFLoader, {}),
            ".md": (UnstructuredMarkdownLoader, {}),
        }

    def _load_single_document(self, file_path: str) -> List[Document]:
        ext = "." + file_path.rsplit(".", 1)[-1]
        if ext in self.ext_to_loader:
            loader_class, loader_args = self.ext_to_loader[ext]
            loader = loader_class(file_path, **loader_args)
            data = loader.load()
            return data
        else:
            raise ValueError(f"Unsupported extension: {ext}")

    def load_documents(self, ignored_files: Set[str] = []) -> List[Document]:
        all_files = []
        for ext in self.ext_to_loader:
            all_files.extend(
                glob.glob(os.path.join(self.parent_dir, f"**/*{ext}"), recursive=True)
            )
        filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]
        print("Files:", filtered_files)
        with Pool(processes=os.cpu_count()) as pool:
            documents = []
            with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
                for i, docs in enumerate(pool.imap_unordered(self._load_single_document, filtered_files)):
                    documents.extend(docs)
                    pbar.update()
        if not documents: print("No documents to loads")
        print(f"Loaded {len(documents)} documents (pages?)")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        all_splits = text_splitter.split_documents(documents)
        print(f"Split into {len(all_splits)} chunks.")
        return all_splits
    
    def create_vectorstore(self, persist_dir: str = "db") -> Chroma:
        model_name = "all-MiniLM-L6-v2.gguf2.f16.gguf"
        gpt4all_kwargs = {'allow_download': 'True'}
        embeddings = GPT4AllEmbeddings(
                model_name=model_name,
                gpt4all_kwargs=gpt4all_kwargs
            )
        if os.path.exists(persist_dir):
            print("Appending to the existing vectorstore")
            vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
            collection = vectorstore.get()
            ignored_files = set([metadata['source'] for metadata in collection['metadatas']])
            texts = self.load_documents(ignored_files)
            if texts: vectorstore.add_documents(texts)
        else:
            print("New vector store.")
            all_splits = self.load_documents()
            print("Creating new embeddings. Will take some minutes ...")
            vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings, persist_directory=persist_dir)
        print("Ingestion complete.")

def main():
    loader = DocumentLoader(parent_dir = "source_files")
    db = loader.create_vectorstore(persist_dir = "db")

if __name__ == "__main__": main()
