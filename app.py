from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import fitz
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import os
import PyPDF2

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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
genai.configure(api_key="AIzaSyC7W5QsVW63nFJjxf5WnI4jhkmzKqMGEAQ")
model = genai.GenerativeModel("gemini-2.0-flash")

PDF_DIR = os.path.abspath("pdfcases")# Folder where PDFs are stored

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages[:2]:  # Extract first 2 pages
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception:
        return "Text extraction failed."

def generate_summary(text):
    if not text or text == "Text extraction failed.":
        return "Summary not available."
    
    prompt = f"""Summarize the following legal case concisely while keeping the key details intact:
    {text}
    """
    
    response = model.generate_content(prompt)
    return response.text if response else "Summary generation failed."

# Endpoint to Retrieve IPC Sections
@app.route("/retrieve_ipc_sections", methods=["POST"])
def retrieve_ipc_sections():
    data = request.json
    query = data.get("query", "")
    top_k = data.get("top_k", 3)
    
    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    query_embedding = embedding_model.encode(query).tolist()
    results = ipc_collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    if results["ids"]:
        retrieved_texts = []
        ipc_numbers = []
        
        for meta in results["metadatas"][0]:
            section_id = meta["section"].replace("IPC_", "").strip()
            description = meta["description"]
            retrieved_texts.append(f"Section {section_id}: {description}")
            ipc_numbers.append(section_id)
        
        return jsonify({"ipc_sections": retrieved_texts, "ipc_numbers": ipc_numbers})
    
    return jsonify({"error": "No relevant IPC section found."}), 404

# Endpoint to Retrieve Case Documents
@app.route("/retrieve_relevant_cases", methods=["POST"])
def retrieve_relevant_cases():
    data = request.json
    ipc_numbers = data.get("ipc_numbers", [])
    top_k = data.get("top_k", 3)

    if not ipc_numbers:
        return jsonify({"error": "IPC numbers list cannot be empty."}), 400

    all_cases = []
    results = case_collection.get()

    if "metadatas" in results:
        for meta in results["metadatas"]:
            if any(ipc in meta.get("ipc_sections", []) for ipc in ipc_numbers):
                pdf_path = os.path.join(PDF_DIR, meta["file_name"])
                extracted_text = extract_text_from_pdf(pdf_path) if os.path.exists(pdf_path) else "Text extraction failed."
                summary = generate_summary(extracted_text)
                all_cases.append({
                    "file_name": meta["file_name"],
                    "path": f"/pdfcases/{meta['file_name']}",
                    "summary": summary
                })

    return jsonify({"cases": all_cases[:top_k]})




# Endpoint to Serve PDF Files
@app.route('/pdfcases/<filename>')
def get_pdf(filename):
    file_path = os.path.join(PDF_DIR, filename)
    
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,  # Forces download
            mimetype="application/pdf",
            download_name=filename  # Suggests the filename
        )
    else:
        return jsonify({"error": "File not found"}), 404

# Function to Generate Legal Response
@app.route("/generate_legal_response", methods=["POST"])
def generate_legal_response():
    data = request.json
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "Query cannot be empty."}), 400
    
    response_data = retrieve_ipc_sections()
    response_json = response_data.get_json()
    
    if "error" in response_json:
        return jsonify({"error": "No relevant IPC sections found."}), 404
    
    retrieved_sections = response_json["ipc_sections"]
    ipc_numbers = response_json["ipc_numbers"]
    
    # Format retrieved sections as input for Gemini
    context = "\n".join(retrieved_sections)
    prompt = f"""Do not apply your own knowledge and use only the provided context. 
    You are a legal assistant. Based on the relevant IPC sections, determine which IPC sections may be applicable to the user and their corresponding punishments.
    Mention the punishments separately.
    User Query: {user_query}
    
    Relevant IPC Sections:
    {context}
    """

    response = model.generate_content(prompt)
    generated_response = response.text.split("\n") if response else "Error generating response."
    
    return jsonify({"response": generated_response, "ipc_numbers": ipc_numbers})

if __name__ == "__main__":
    app.run(debug=True)
