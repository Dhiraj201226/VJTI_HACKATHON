import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8080/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

export const initiateDraft = async (params) => {
    // Check if params is string (old way) or object (new way)
    const data = typeof params === 'string' ? { objective: params, language: "Marathi" } : params;
    const response = await apiClient.post('/draft/initiate', data);
    return response.data;
};

export const generateDraft = async (objective, officerDecisions, language = "Marathi") => {
    const response = await apiClient.post('/draft/generate', {
        objective,
        officer_decisions: officerDecisions,
        language
    });
    return response.data;
};

export const checkLegalCompliance = async (grJson) => {
    const response = await apiClient.post('/draft/legal_review', grJson);
    return response.data;
};

export const askFAQ = async (question) => {
    const response = await apiClient.post('/faq/ask', { question });
    return response.data;
};

export const getRagStats = async () => {
    const response = await apiClient.get('/rag/stats');
    return response.data;
};

export const uploadAndExtractText = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/draft/extract_text', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getDraftHistory = async () => {
    const response = await apiClient.get('/draft/history');
    return response.data;
};

export default apiClient;
