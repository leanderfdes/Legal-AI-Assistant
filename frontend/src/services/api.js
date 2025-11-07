import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"

// Retrieve IPC Sections
export const getIPCSections = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/retrieve_ipc_sections`, { query });
    return response.data;
  } catch (error) {
    console.error("Error fetching IPC sections:", error);
    return null;
  }
};

// Retrieve Relevant Cases
export const getRelevantCases = async (ipcNumbers) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/retrieve_relevant_cases`, { ipc_numbers: ipcNumbers });
      return response.data.cases; // Ensure response contains case summaries
    } catch (error) {
      console.error("Error fetching relevant cases:", error);
      return [];
    }
  };

// Generate Legal Response
export const generateLegalResponse = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/generate_legal_response`, { query });
    return response.data;
  } catch (error) {
    console.error("Error generating legal response:", error);
    return null;
  }
};
