# AIzaSyDs2zuNE3jG4TraBg98PZlOmYsbxFkQ-Bk api key
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Initialize FastAPI app
app = FastAPI()

# Load Local Embedding Model
embedding_model_path = "./models/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(embedding_model_path)

# Load ChromaDB (Vector Database)
ipc_chroma_path = "./vector_db"
case_chroma_path = "./case_vector_db"

ipc_chroma_client = chromadb.PersistentClient(path=ipc_chroma_path)
case_chroma_client = chromadb.PersistentClient(path=case_chroma_path)

ipc_collection = ipc_chroma_client.get_collection(name="ipc_sections")
case_collection = case_chroma_client.get_collection(name="case_documents")

# Configure Gemini API
genai.configure(api_key="AIzaSyDs2zuNE3jG4TraBg98PZlOmYsbxFkQ-Bk")
model = genai.GenerativeModel("gemini-2.0-flash")

# Request Model for IPC Retrieval
class IPCQuery(BaseModel):
    query: str
    top_k: int = 3

# Request Model for Case Retrieval
class CaseQuery(BaseModel):
    ipc_numbers: list[str]
    top_k: int = 3

# Endpoint to Retrieve IPC Sections
@app.post("/retrieve_ipc_sections")
def retrieve_ipc_sections(request: IPCQuery):
    query_embedding = embedding_model.encode(request.query).tolist()
    results = ipc_collection.query(query_embeddings=[query_embedding], n_results=request.top_k)
    
    if results["ids"]:
        retrieved_texts = []
        ipc_numbers = []
        
        for meta in results["metadatas"][0]:
            section_id = meta["section"].replace("IPC_", "").strip()
            description = meta["description"]
            retrieved_texts.append(f"Section {section_id}: {description}")
            ipc_numbers.append(section_id)
        
        return {"ipc_sections": retrieved_texts, "ipc_numbers": ipc_numbers}
    
    raise HTTPException(status_code=404, detail="No relevant IPC section found.")

# Endpoint to Retrieve Case Documents
@app.post("/retrieve_relevant_cases")
def retrieve_relevant_cases(request: CaseQuery):
    all_cases = []
    
    for ipc_section in request.ipc_numbers:
        results = case_collection.get()
        
        if "metadatas" in results:
            for meta in results["metadatas"]:
                if "ipc_sections" in meta and ipc_section in meta["ipc_sections"]:
                    all_cases.append({"file_name": meta["file_name"], "path": meta["path"]})
    
    return {"cases": all_cases[:request.top_k]}

# Function to Generate Legal Response
def generate_response(user_query):
    """Generate a legal response using retrieved IPC sections and Gemini API."""
    retrieved_sections, ipc_numbers = retrieve_ipc_sections(user_query)

    # ✅ Ensure clean IPC section numbers
    ipc_numbers = [sec.replace("IPC_", "").strip() for sec in ipc_numbers]

    # 🔹 Print extracted IPC section numbers for debugging
    print("✅ Cleaned IPC Sections for Retrieval:", ipc_numbers)

    # 🔹 Format retrieved sections as input for Gemini
    context = "\n".join(retrieved_sections)
    prompt = f"""Do not apply your own knowledge and use only the provided context. 
    You are a legal assistant. Based on the relevant IPC sections, determine which IPC sections may be applicable to the user and their corresponding punishments.
    mention the punishments separately.
    User Query: {user_query}
    
    Relevant IPC Sections:
    {context}
    """

    # 🔹 Call Gemini API for LLM response
    response = model.generate_content(prompt)

    return response.text if response else "Error generating response.", ipc_numbers

