import React, { useState } from "react";
import axios from "axios";
import "./IpcLegalAssistant.css"; // Import CSS file

const IPCLegalAssistant = () => {
  const [query, setQuery] = useState("");
  const [ipcResults, setIpcResults] = useState([]);
  const [caseResults, setCaseResults] = useState([]);
  const [legalResponse, setLegalResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const ipcData = await axios.post("http://127.0.0.1:5000/retrieve_ipc_sections", { query, top_k: 3 });

      if (ipcData.data && ipcData.data.ipc_sections) {
        setIpcResults(ipcData.data.ipc_sections);

        const caseData = await axios.post("http://127.0.0.1:5000/retrieve_relevant_cases", { ipc_numbers: ipcData.data.ipc_numbers, top_k: 3 });

        if (caseData.data && caseData.data.cases) {
          setCaseResults(caseData.data.cases);
        }

        const responseData = await axios.post("http://127.0.0.1:5000/generate_legal_response", { query });

        if (responseData.data && responseData.data.response) {
          setLegalResponse(responseData.data.response);
        }
      } else {
        setIpcResults([]);
        setCaseResults([]);
        setLegalResponse("No relevant IPC sections found.");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setLegalResponse("An error occurred while processing your request.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`container ${darkMode ? "dark-mode" : ""}`}>
      {/* Dark Mode Toggle Button */}
      <button className="toggle-button" onClick={toggleDarkMode}>
        {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
      </button>

      {/* Card Container */}
      <div className="card">
        <h2 className="title">IPC Legal Assistant</h2>

        {/* Input Field */}
        <input
          type="text"
          placeholder="Enter your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="input"
        />

        {/* Search Button */}
        <button onClick={handleSearch} disabled={loading} className="search-button">
          {loading ? "Processing..." : "Search"}
        </button>

        {/* Case Documents Section */}
        <h3 className="section-title">Relevant Case Documents:</h3>
        <ul className="list">
          {caseResults.map((caseItem, index) => (
            <li key={index} className="list-item">
              <a 
  href={`http://127.0.0.1:5000/pdfcases/${caseItem.file_name}`} 
  download={caseItem.file_name} 
  className="case-link"
>
  {caseItem.file_name}
</a>
              <p className="case-summary">{caseItem.summary}</p>
            </li>
          ))}
        </ul>

        {/* IPC Sections & Punishments */}
        <h3 className="section-title">Applicable Sections and Punishments:</h3>
        <ul className="list">
          {String(legalResponse)
            .replace(/\*\*/g, "\n")
            .split("\n")
            .map((point, index) =>
              point.trim() ? (
                <li key={index} className="list-item">{point}</li>
              ) : null
            )}
        </ul>
      </div>
    </div>
  );
};

export default IPCLegalAssistant;
