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
openai_api_key = os.getenv("OPENAI_API_KEY")
llm_client = OpenAI(api_key=openai_api_key)

# Load embedding model
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# Connect to Qdrant vector database
vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="chai_docs",
    url="http://localhost:6333"
)

# Function to process user question
def generate_response_from_documents(user_question: str):
    search_results = vector_db.similarity_search(query=user_question, k=5)

    context = "\n\n\n".join([
        f"Page Content: {doc.page_content}\n"
        f"Section: {doc.metadata.get('section', 'N/A')}\n"
        f"Sub-section: {doc.metadata.get('sub_section', 'N/A')}\n"
        f"url: {doc.metadata.get('url', 'N/A')}"
        for doc in search_results
    ])

    system_prompt = """
        You are a helpful assistant that gives detailed, accurate answers based on the provided document context.

        If you find relevant information in the context, answer the question clearly and concisely.
        If not, say: "I couldn’t find the answer from chaidocs."

        Always mention the section, subsection and url (to navigate) where relevant information was found.

        Output Format in JSON:
        {
            "Answer": "<Give your detailed answer>",
            "Code": "<if necessary from context>",
            "Section": "<Relevant section from context>",
            "Sub_section": "<Relevant sub-section from context>",
            "url": "<Relevant URL from context>"
        }
    """

    user_prompt = f"""
        Use the following context to answer the question.
        Context: {context}
        Question: {user_question}
    """

    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


# Initialize FastAPI app
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class QuestionRequest(BaseModel):
    question: str


# API endpoint to handle query
@app.post("/query")
async def handle_question(request: QuestionRequest):
    try:
        response_content = generate_response_from_documents(request.question)
        return json.loads(response_content)
    except Exception as e:
        return {"error": str(e)}


# Start the app (for direct run)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat:app", host="127.0.0.1", port=8000, reload=True)
