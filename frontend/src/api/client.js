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

export default apiClient;
