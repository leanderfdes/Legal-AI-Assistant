# ⚖️ AI-Powered Legal Decision Support System  

> 🧠 An advanced AI-driven system that predicts relevant IPC sections, estimates punishments, and retrieves similar past cases — helping law enforcement and judicial professionals make accurate, data-driven decisions.  

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![NLP](https://img.shields.io/badge/NLP-AI%20Driven-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Overview  

The **AI-Powered Legal Decision Support System** integrates Artificial Intelligence into India’s legal ecosystem.  
It predicts applicable **Indian Penal Code (IPC)** sections, suggests corresponding punishments, and retrieves **semantically similar past cases**.  
Built with modern AI tools like **SentenceTransformer**, **ChromaDB**, and **Gemini API**, it provides faster and more accurate legal analysis.

---

## 🧩 Tech Stack  

| Category | Technologies Used |
|-----------|-------------------|
| **Frontend** | React.js, HTML5, CSS3 |
| **Backend** | Flask (Python) |
| **AI / NLP** | SentenceTransformer, NLTK, Scikit-learn |
| **Database** | ChromaDB (Vector Database) |
| **APIs** | Google Gemini API |
| **Utilities** | Pandas, NumPy, PyPDF2 |
| **Version Control** | Git & GitHub |

---

## ⚙️ Features  

- 🔍 **IPC Section Prediction** – Automatically identifies applicable IPC sections from crime descriptions.  
- ⚖️ **Punishment Estimation** – Suggests punishments aligned with legal precedents.  
- 📚 **Case Retrieval** – Finds and displays similar past cases using semantic search.  
- 💬 **AI Summarization** – Provides concise summaries via **Gemini API**.  
- 🧠 **Context-Aware Classification** – Handles first-person, third-person, and mixed legal narratives.  

---

## 🧱 System Architecture  

Crime Description
↓
SentenceTransformer → Text Embeddings
↓
ChromaDB → Semantic Search
↓
Prediction Model → IPC Sections + Punishments
↓
Gemini API → Case Summaries
↓
Frontend UI → Interactive Results Display

---

## 💻 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/AI-Legal-Decision-Support.git
cd AI-Legal-Decision-Support
