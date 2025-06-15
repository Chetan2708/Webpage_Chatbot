from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY is not set in the environment.")
    raise EnvironmentError("Missing OPENAI_API_KEY in environment.")

openai_client = OpenAI(api_key= api_key)

# Use OpenAI Embeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# Connect to Qdrant
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="chai_docs",
    url="http://localhost:6333",
)


# Process user query
def process_query(query: str):
    
    search_results = vector_store.similarity_search(query=query, k=5)
    context = "\n\n\n".join([
        f"Page Content: {result.page_content}\nSection: {result.metadata['section']}\nSub-section: {result.metadata['sub_section']}\nurl: {result.metadata['url']}"
        for result in search_results
    ])

    SYSTEM_PROMPT = """
        You are a helpful assistant that gives detailed, accurate answers based on the provided document context.
        
        If you find relevant information in the context, answer the question clearly and concisely.
        If not, say: "I couldn’t find the answer from chaidocs."
        
        Output Format in JSON:
        {
            "Answer": "<Give your detailed answer>",
            "Code": "<if necessary from context>",
            "Section": "<Relevant section from context>",
            "Sub_section": "<Relevant sub-section from context>",
            "url": "<Relevant URL from context>"
        }
    """


    USER_PROMPT = f"""
        Use the following context to answer the question.
        Context: {context}
        Question: {query}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        response_format={"type": "json_object"}, 
    )

    content = response.choices[0].message.content
    if "I couldn’t find the answer from chaidocs." in content:
        return json.dumps({
            "Answer": "I couldn’t find the answer from chaidocs.",
            "Code": "",
            "Section": "",
            "Sub_section": "",
            "url": ""
        })

    return content
    


# FastAPI App
app = FastAPI()

# Allow all origins (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class Query(BaseModel):
    question: str


# POST /query endpoint
@app.post("/query")
async def ask(query: Query):
    response = process_query(query.question)
    return json.loads(response)


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat:app", host="127.0.0.1", port=8000, reload=True)
