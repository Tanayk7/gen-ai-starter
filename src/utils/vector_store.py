import os
import importlib
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_openai_embedding(text: str) -> np.ndarray:
    """
    Get the embedding of a text using OpenAI's embedding model.

    Args:
        text (str): The text to be embedded.

    Returns:
        np.ndarray: The embedding of the text as a numpy array.
    """
    import openai
    text = text.replace("\n", " ")
    embedding = openai.OpenAI().embeddings.create(
        input=[text],
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    ).data[0].embedding
    return np.array(embedding, dtype=np.float32)

class GenericVectorStore:
    def __init__(self):
        """
        Initialize the GenericVectorStore with the specified vector store type.

        The vector store type is determined by the environment variable 'VECTOR_STORE_TYPE'.
        Supported types are 'chroma', 'pinecone', and 'faiss'.
        """
        self.vector_store_type = os.getenv("VECTOR_STORE_TYPE", "chroma").lower()
        self.vectorstore = self._load_vector_store()

    def _load_vector_store(self):
        """
        Load the appropriate vector store based on the vector store type.

        Returns:
            The initialized vector store object.

        Raises:
            ValueError: If the vector store type is unsupported.
        """
        if self.vector_store_type == 'chroma':
            chromadb = importlib.import_module("chromadb")
            client = chromadb.Client()
            collection_name = os.getenv("CHROMA_COLLECTION_NAME", "default")
            return client.get_or_create_collection(name=collection_name)

        elif self.vector_store_type == 'pinecone':
            pinecone = importlib.import_module("pinecone")
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENV")
            )
            index_name = os.getenv("PINECONE_INDEX_NAME")
            return pinecone.Index(index_name)

        elif self.vector_store_type == 'faiss':
            import faiss
            dim = int(os.getenv("FAISS_DIM", 3072))  # Make sure this matches your embedding size
            index = faiss.IndexFlatL2(dim)
            self.faiss_index = index
            self.faiss_texts = []
            self.faiss_metadatas = []
            self.faiss_ids = []
            return index

        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")

    def insert_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """
        Insert documents into the vector store.

        Args:
            texts (List[str]): The list of document texts to insert.
            metadatas (Optional[List[Dict]], optional): Metadata associated with each document. Defaults to None.
            ids (Optional[List[str]], optional): Unique identifiers for each document. Defaults to None.
        """
        vectors = [get_openai_embedding(text) for text in texts]

        if self.vector_store_type == "chroma":
            self.vectorstore.add(
                embeddings=vectors,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

        elif self.vector_store_type == "pinecone":
            to_upsert = [
                (ids[i], vectors[i], metadatas[i] if metadatas else {})
                for i in range(len(texts))
            ]
            self.vectorstore.upsert(vectors=to_upsert)

        elif self.vector_store_type == "faiss":
            vec_array = np.vstack(vectors)
            self.vectorstore.add(vec_array)
            self.faiss_texts.extend(texts)
            self.faiss_metadatas.extend(metadatas if metadatas else [{}] * len(texts))
            self.faiss_ids.extend(ids if ids else [str(len(self.faiss_ids) + i) for i in range(len(texts))])

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a similarity search in the vector store.

        Args:
            query (str): The query text to search for.
            top_k (int, optional): The number of top results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of search results with document details and distances.
        """
        vector = get_openai_embedding(query).reshape(1, -1)

        if self.vector_store_type == "chroma":
            return self.vectorstore.query(query_embeddings=vector, n_results=top_k)

        elif self.vector_store_type == "pinecone":
            return self.vectorstore.query(vector=vector[0], top_k=top_k, include_metadata=True)

        elif self.vector_store_type == "faiss":
            distances, indices = self.vectorstore.search(vector, top_k)
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                results.append({
                    "id": self.faiss_ids[idx],
                    "text": self.faiss_texts[idx],
                    "metadata": self.faiss_metadatas[idx],
                    "distance": distances[0][i]
                })
            return results

    def delete_documents(self, ids: List[str]):
        """
        Delete documents from the vector store by their IDs.

        Args:
            ids (List[str]): The list of document IDs to delete.

        Raises:
            NotImplementedError: If deletion is not supported for the vector store type.
        """
        if self.vector_store_type == "chroma":
            self.vectorstore.delete(ids)

        elif self.vector_store_type == "pinecone":
            self.vectorstore.delete(ids=ids)

        elif self.vector_store_type == "faiss":
            raise NotImplementedError("Manual deletion in raw FAISS setup is not implemented")

    def retrieve(self, ids: List[str]):
        """
        Retrieve documents from the vector store by their IDs.

        Args:
            ids (List[str]): The list of document IDs to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of retrieved documents with their details.
        """
        if self.vector_store_type == "chroma":
            return self.vectorstore.get(ids=ids)

        elif self.vector_store_type == "pinecone":
            return self.vectorstore.fetch(ids=ids)

        elif self.vector_store_type == "faiss":
            results = []
            for idx in ids:
                if idx in self.faiss_ids:
                    i = self.faiss_ids.index(idx)
                    results.append({
                        "id": self.faiss_ids[i],
                        "text": self.faiss_texts[i],
                        "metadata": self.faiss_metadatas[i]
                    })
            return results
