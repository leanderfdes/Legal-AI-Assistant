import streamlit as st
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# 🔹 Streamlit Page Configuration
st.set_page_config(page_title="IPC Legal Assistant", layout="wide")

# 🔹 Load Local Embedding Model
embedding_model_path = "./models/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(embedding_model_path)

# 🔹 Load ChromaDB (Prebuilt Vector Database)
chroma_path = "./vector_db"
chroma_client = chromadb.PersistentClient(path=chroma_path)
collection = chroma_client.get_collection(name="ipc_sections")

# 🔹 Configure Gemini API
genai.configure(
    api_key="AIzaSyC7W5QsVW63nFJjxf5WnI4jhkmzKqMGEAQ"
)  # Replace with your actual API key
model = genai.GenerativeModel("gemini-2.0-flash")


def retrieve_ipc_sections(query, top_k=5):
    """Retrieve the most relevant IPC sections based on a query."""
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    if results["ids"]:
        retrieved_texts = [
            f"Section {meta['section']}: {meta['description']}"
            for meta in results["metadatas"][0]
        ]
        return retrieved_texts
    return ["No relevant IPC section found."]


def generate_response(user_query):
    """Generate a legal response using retrieved IPC sections and Gemini API."""
    retrieved_sections = retrieve_ipc_sections(user_query)

    # 🔹 Format retrieved sections as input for Gemini
    context = "\n".join(retrieved_sections)
    prompt = f"""do not apply your own knowledge and use only context provided and frame response!. You are a legal assistant. Based on the relevant ipc sections mention what ipc sections may be applicable on the user and relevant punishments considering the following scenario: mention the punishments seperately
    

    User Query: {user_query}
    
    Relevant IPC Sections:
    {context}
    
    """

    # 🔹 Call Gemini API for LLM response
    response = model.generate_content(prompt)

    return response.text if response else "Error generating response."


# 🔹 Streamlit UI
st.title("🔍 IPC Legal Assistant")
st.write("Enter a scenario to find relevant IPC sections and legal analysis.")

# User Input
user_query = st.text_area(
    "Describe the incident:", placeholder="E.g., I robbed a house"
)

if st.button("Find Applicable IPC Sections"):
    if user_query.strip():
        with st.spinner("Retrieving legal insights..."):
            response = generate_response(user_query)

        st.subheader("📜 Applicable IPC Sections & Analysis")
        st.write(response)
    else:
        st.warning("Please enter a scenario to proceed.")

st.markdown("---")
st.markdown("🔹 Built using **local embeddings**, **ChromaDB**, and **Gemini API**.")
