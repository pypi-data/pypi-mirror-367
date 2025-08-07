from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_yugabytedb import YBEngine, YugabyteDBVectorStore

# Replace the connection string with your own YugabyteDB connection string
CONNECTION_STRING = "postgresql+psycopg://yugabyte:@localhost:5433/yugabyte"
engine = YBEngine.from_connection_string(url=CONNECTION_STRING)

# Replace the vector size with your own vector size
VECTOR_SIZE = 768
embedding = DeterministicFakeEmbedding(size=VECTOR_SIZE)

TABLE_NAME = "my_doc_collection"

engine.init_vectorstore_table(
    table_name=TABLE_NAME,
    vector_size=VECTOR_SIZE,
)

store = YugabyteDBVectorStore.create_sync(
    engine=engine,
    table_name=TABLE_NAME,
    embedding_service=embedding,
)

docs = [
    Document(page_content="Apples and oranges"),
    Document(page_content="Cars and airplanes"),
    Document(page_content="Train")
]

store.add_documents(docs)

query = "I'd like a fruit."
docs = store.similarity_search(query)
print(docs)