from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from urls_extraction import extract_valid_links
from openai import OpenAI
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY is not set in the environment.")
    raise EnvironmentError("Missing OPENAI_API_KEY in environment.")
openai_client = OpenAI(api_key=api_key)

# Set up OpenAI embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# Configure document splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=200
)

# Qdrant configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "chai_docs"

def extract_metadata_from_url(url: str) -> dict:
    segments = url.strip("/").split("/")
    return {
        "section": segments[-3] if len(segments) >= 3 else "unknown",
        "sub_section": segments[-2] if len(segments) >= 2 else "unknown",
        "url": url
    }

def index_documents_from_urls():
    urls = extract_valid_links()
    if not urls:
        print("⚠️ No URLs found to process.")
        return

    for index, url in enumerate(urls, start=1):
        print(f"\n🔄 [{index}] Processing: {url}")

        try:
            # Load the page content
            loader = WebBaseLoader(url)
            documents = loader.load()

            # Add metadata
            metadata = extract_metadata_from_url(url)
            for doc in documents:
                doc.metadata.update(metadata)

            # Split documents
            chunks = text_splitter.split_documents(documents)

            # Store in Qdrant
            QdrantVectorStore.from_documents(
                documents=chunks,
                url=QDRANT_URL,
                collection_name=COLLECTION_NAME,
                embedding=embedding_model
            )

            print(f"✅ Indexed {len(chunks)} chunks from: {url}")

        except Exception as e:
            print(f"❌ Failed to process [{index}] {url}: {str(e)}")

if __name__ == "__main__":
    index_documents_from_urls()
