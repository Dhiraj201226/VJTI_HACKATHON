import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

export const initiateDraft = async (objective) => {
    const response = await apiClient.post('/draft/initiate', { objective });
    return response.data;
};

export const generateDraft = async (objective, officerDecisions) => {
    const response = await apiClient.post('/draft/generate', {
        objective,
        officer_decisions: officerDecisions
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

export default apiClient;
