import os
import PyPDF2
import chromadb
import google.generativeai as genai
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 🔹 Configure Gemini API
genai.configure(
    api_key="AIzaSyC7W5QsVW63nFJjxf5WnI4jhkmzKqMGEAQ"
)  # Replace with your actual API key
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# 🔹 Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Define Paths
INPUT_FOLDER = r"pdfcases"
CHROMA_PATH = "./case_vector_db"

# 🔹 Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
case_collection = chroma_client.get_or_create_collection(
    name="case_documents"
)  # ✅ Corrected definition


# 🔹 Function to Extract Text from PDFs
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
    return text.strip()


# 🔹 Function to Extract IPC Sections Using Gemini API
def extract_ipc_with_gemini(text):
    """Extract IPC sections from legal document text using Gemini API."""
    prompt = f"""
    Extract all IPC sections from the following legal document.
    - Return only section numbers (e.g., 498A, 304B, 34).
    - If a section contains subparts (e.g., 376(2)(g)), format it as "376-2-g".
    - Ensure output is **only a comma-separated list** with no extra text.

    Example Output:
    498A, 304B, 34, 376-2-g, 147, 148

    Document Text:
    {text}
    """

    response = gemini_model.generate_content(prompt)

    if response and response.text:
        extracted_text = response.text.strip()
        ipc_numbers = [
            sec.strip().replace("(", "-").replace(")", "").replace("/", "-")
            for sec in extracted_text.split(",")
            if sec.strip()
        ]
        return sorted(list(set(ipc_numbers)))  # ✅ Sort & remove duplicates

    return []


# 🔹 Function to Store All PDFs in ChromaDB & Print Stored Data
def store_pdfs_in_chromadb():
    """Extract IPC sections from PDFs and store them in ChromaDB."""
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDF files found in the input folder!")
        return

    print(
        f"📂 Found {len(pdf_files)} PDFs. Extracting IPC Sections & Storing in ChromaDB..."
    )

    # ✅ Fetch existing document IDs to prevent duplicates
    existing_ids = (
        set(case_collection.get()["ids"]) if case_collection.count() > 0 else set()
    )

    for pdf_file in tqdm(pdf_files, desc="Indexing PDFs"):
        if pdf_file in existing_ids:
            print(f"⚠️ Skipping {pdf_file} (Already in database)")
            continue  # Skip duplicate entries

        pdf_path = os.path.join(INPUT_FOLDER, pdf_file)
        text = extract_text_from_pdf(pdf_path)

        if not text:
            print(f"⚠️ Skipping {pdf_file} (No extractable text)")
            continue

        ipc_sections = extract_ipc_with_gemini(text)
        if not ipc_sections:
            print(f"⚠️ Skipping {pdf_file} (No IPC sections extracted)")
            continue

        ipc_sections_str = ", ".join(ipc_sections)

        try:
            embedding = embedding_model.encode(text).tolist()
        except:
            embedding = np.zeros(384).tolist()

        case_collection.add(
            ids=[pdf_file],
            embeddings=[embedding],
            metadatas=[
                {
                    "file_name": pdf_file,
                    "path": pdf_path,
                    "ipc_sections": ipc_sections_str,
                }
            ],
        )

        print(f"✅ Stored: {pdf_file} → IPC Sections: {ipc_sections_str}")

    print("✅ All PDFs have been indexed successfully!")


# 🔹 Function to Print Stored Metadata from ChromaDB
def view_stored_cases():
    """View stored case document metadata in ChromaDB."""
    results = case_collection.get()

    if "ids" in results and results["ids"]:
        print("\n📊 **Stored Case Documents in ChromaDB:**")
        for meta in results["metadatas"]:
            print(f"\n📂 **File:** {meta['file_name']}")
            print(f"📍 **Path:** {meta['path']}")
            print(f"📜 **IPC Sections Stored:** {meta['ipc_sections']}")
    else:
        print("⚠️ No case documents found in ChromaDB!")


# 🔹 Run the Storage Process
if __name__ == "__main__":
    store_pdfs_in_chromadb()
    view_stored_cases()  # ✅ Print stored cases for verification
# 📂 **File:** State_vs_Dinesh_Mohaniya_Ors_on_30_June_2023.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Dinesh_Mohaniya_Ors_on_30_June_2023.PDF
# 📜 **IPC Sections Stored:** 354, 34, 354B, 341, 323

# 📂 **File:** State_vs_Karna_Bachkanda_on_23_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Karna_Bachkanda_on_23_December_2024.PDF
# 📜 **IPC Sections Stored:** 304, 34, 302

# 📂 **File:** State_vs_Manoj_on_24_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Manoj_on_24_December_2024.PDF
# 📜 **IPC Sections Stored:** 325, 319, 34, 174A, 320, 323

# 📂 **File:** State_vs_Mehraj_on_17_January_2023.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Mehraj_on_17_January_2023.PDF
# 📜 **IPC Sections Stored:** 325, 320, 323, 377

# 📂 **File:** State_vs_Pardeep_Kumar_on_19_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Pardeep_Kumar_on_19_December_2024.PDF
# 📜 **IPC Sections Stored:** 304B, 498A, 34, 406

# 📂 **File:** State_vs_Shahid_on_23_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Shahid_on_23_December_2024.PDF
# 📜 **IPC Sections Stored:** 341, 323

# 📂 **File:** State_vs_Sudhir_Kumar_on_24_December_2024 (1).PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Sudhir_Kumar_on_24_December_2024 (1).PDF
# 📜 **IPC Sections Stored:** 304B, 498A, 34, 306

# 📂 **File:** State_vs_Sudhir_Kumar_on_24_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\State_vs_Sudhir_Kumar_on_24_December_2024.PDF
# 📜 **IPC Sections Stored:** 304B, 498A, 34, 306

# 📂 **File:** Sulabh_Gupta_vs_State_Nct_Of_Delhi_Anr_on_18_July_2023.PDF
# 📍 **Path:** F:\pdl\pdfcases\Sulabh_Gupta_vs_State_Nct_Of_Delhi_Anr_on_18_July_2023.PDF
# 📜 **IPC Sections Stored:** 420, 34, 498A, 406, 377, 506

# 📂 **File:** Surendra_Singh_vs_The_State_Of_Rajasthan_on_11_April_2023.PDF
# 📍 **Path:** F:\pdl\pdfcases\Surendra_Singh_vs_The_State_Of_Rajasthan_on_11_April_2023.PDF
# 📜 **IPC Sections Stored:** 149, 325, 34, 308, 302, 147, 427, 341, 323

# 📂 **File:** Surinder_Singh_Oberoi_vs_Mahesh_Kumar_on_23_December_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\Surinder_Singh_Oberoi_vs_Mahesh_Kumar_on_23_December_2024.PDF
# 📜 **IPC Sections Stored:** 338, 279

# 📂 **File:** The_State_Of_Himachal_Pradesh_vs_Raghubir_Singh_on_15_May_2024.PDF
# 📍 **Path:** F:\pdl\pdfcases\The_State_Of_Himachal_Pradesh_vs_Raghubir_Singh_on_15_May_2024.PDF
# 📜 **IPC Sections Stored:** 313, 376, 375, 34, 376(2)(g)

# 📂 **File:** The_State_Of_Uttar_Pradesh_vs_Subhash_Pappu_on_1_April_2022 (1).PDF
# 📍 **Path:** F:\pdl\pdfcases\The_State_Of_Uttar_Pradesh_vs_Subhash_Pappu_on_1_April_2022 (1).PDF
# 📜 **IPC Sections Stored:** 148, 149, 304, 302, 147, 324, 323

# 📂 **File:** The_State_Of_Uttar_Pradesh_vs_Subhash_Pappu_on_1_April_2022.PDF
# 📍 **Path:** F:\pdl\pdfcases\The_State_Of_Uttar_Pradesh_vs_Subhash_Pappu_on_1_April_2022.PDF
# 📜 **IPC Sections Stored:** 148, 149, 304, 302, 147, 324, 323
