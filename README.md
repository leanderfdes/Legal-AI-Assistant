# ⚖️ AI-Powered Legal Decision Support System  

> 🧠 *Empowering justice through Artificial Intelligence.*  
> A cutting-edge AI system that predicts relevant IPC sections, estimates punishments, and retrieves similar past cases — enabling law enforcement officers, legal professionals, and judges to make informed, data-driven decisions with speed and accuracy.  

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![NLP](https://img.shields.io/badge/NLP-AI%20Driven-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Build](https://img.shields.io/badge/Build-Stable-brightgreen)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-blue)

---

## 🚀 Overview  

The **AI-Powered Legal Decision Support System** leverages Artificial Intelligence to revolutionize India’s criminal justice process.  
It analyzes crime descriptions to predict applicable **Indian Penal Code (IPC)** sections, recommend **appropriate punishments**, and retrieve **semantically similar past cases**.  

By integrating **SentenceTransformer**, **ChromaDB**, and **Google’s Gemini API**, the system bridges the gap between unstructured legal text and actionable insights — ensuring faster, fairer, and more consistent judicial outcomes.  

---

## 🧠 Core Objectives  

- ⚖️ Automate **IPC section classification** using advanced NLP.  
- 🔍 Estimate **appropriate punishments** aligned with legal precedents.  
- 📚 Retrieve **relevant historical cases** for judicial reference.  
- 🚔 Assist **law enforcement** in accurate and efficient FIR filing.  
- 👩‍⚖️ Support **judges and legal analysts** in data-driven decision-making.  

---

## 🧩 Tech Stack  

| Category | Technologies Used |
|-----------|-------------------|
| **Frontend** | React.js, HTML5, CSS3 |
| **Backend** | Flask (Python) |
| **AI / NLP** | SentenceTransformer, NLTK, Scikit-learn |
| **Database** | ChromaDB (Vector Database) |
| **API & Integration** | Google Gemini API |
| **Utilities** | Pandas, NumPy, PyPDF2 |
| **Version Control** | Git & GitHub |

---

## 🌟 Key Features  

- 🔍 **IPC Section Prediction** – Identifies relevant IPC sections from textual descriptions.  
- ⚖️ **Punishment Estimation** – Suggests punishment ranges based on past judicial data.  
- 📚 **Case Retrieval** – Retrieves and ranks similar past cases using semantic search.  
- 💬 **AI Summarization** – Generates concise summaries of retrieved legal cases via **Gemini API**.  
- 🧠 **Context-Aware NLP** – Handles first-person, third-person, and mixed legal narratives for robust prediction.  
- 📈 **Performance Optimized** – Achieved up to **77.63% accuracy** in IPC classification tasks.  

---

## 🧱 System Architecture  
  
```bash
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
```
---

## 💻 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/AI-Legal-Decision-Support.git
cd AI-Legal-Decision-Support
