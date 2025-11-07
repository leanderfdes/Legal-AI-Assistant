from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import logging
import json
import chromadb

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Gemini API
genai.configure(api_key="AIzaSyC7W5QsVW63nFJjxf5WnI4jhkmzKqMGEAQ")  # Replace with actual API key
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_response(user_query):
    """Use Gemini to generate a response with concise IPC sections, punishments, and case details."""
    prompt = f"""
    You are a legal assistant. Based on the user's query, determine the relevant IPC sections, 
    provide a concise rephrased description, specify punishments, and suggest past cases.
    
    User Query: {user_query}
    
    Provide the response in JSON format with the following keys:
    - ipc_sections: A list of objects containing 'section', 'concise_description', and 'punishment'.
    - case_sections: A list of IPC sections for relevant cases.
    """
    
    response = model.generate_content(prompt)
    
    if response and response.text:
        try:
            response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            response_json = json.loads(response_text)
            
            # Retrieve relevant cases
            case_sections = response_json.get("case_sections", [])
            case_details = []
            
            for section in case_sections:
                retrieved_cases = retrieve_relevant_cases(section)
                for case in retrieved_cases:
                    file_path = case["path"]
                    case_summary = summarize_pdf(file_path)
                    case_details.append({"file_name": case["file_name"], "summary": case_summary})
            
            response_json["case_details"] = case_details
            del response_json["case_sections"]  # Remove old links
            
            return response_json
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {e}")
            return {"error": "Failed to parse AI response."}
    
    return {"error": "Error generating response."}

def retrieve_relevant_cases(ipc_section):
    """Retrieve case documents where metadata contains the exact IPC section."""
    results = case_collection.get()  # Fetch all stored cases

    retrieved_cases = []
    if "metadatas" in results:
        for meta in results["metadatas"]:
            if "ipc_sections" in meta and ipc_section in meta["ipc_sections"].split(", "):
                retrieved_cases.append({"file_name": meta["file_name"], "path": meta["path"]})
    
    return retrieved_cases

def summarize_pdf(file_path):
    """Summarize the content of a PDF file using Gemini."""
    try:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        
        if not text.strip():
            return "Summary not available: PDF contains no extractable text."
        
        prompt = f"Summarize the following legal document:\n{text}"
        response = model.generate_content(prompt)
        return response.text if response else "Summary not available."
    
    except Exception as e:
        logging.error(f"Error summarizing PDF: {str(e)}")
        return f"Error summarizing document: {str(e)}"

@app.route('/generate_response', methods=['POST'])
def generate_response_endpoint():
    data = request.json
    user_query = data.get('user_query')
    if not user_query:
        return jsonify({"error": "User query is required"}), 400

    response = generate_response(user_query)
    return jsonify(response)

@app.route('/summarize_pdf', methods=['POST'])
def summarize_pdf_endpoint():
    data = request.json
    file_name = data.get('file_name')
    if not file_name:
        return jsonify({"error": "File name is required"}), 400
    
    file_path = os.path.join("cases", file_name)  # Assuming cases are stored in a 'cases' folder
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    summary = summarize_pdf(file_path)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
