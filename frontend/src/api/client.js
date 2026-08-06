import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8080/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

export const getAvailableModels = async (provider) => {
    const response = await apiClient.get(`/models?provider=${provider}`);
    return response.data;
};

export const initiateDraft = async (params) => {
    const provider = localStorage.getItem('llmProvider') || 'groq';
    const model = localStorage.getItem('llmModel') || '';
    const data = typeof params === 'string' 
        ? { objective: params, language: "Marathi", llm_provider: provider, llm_model: model } 
        : { ...params, llm_provider: provider, llm_model: model };
    const response = await apiClient.post('/draft/initiate', data);
    return response.data;
};

export const generateDraft = async (objective, officerDecisions, language = "Marathi") => {
    const provider = localStorage.getItem('llmProvider') || 'groq';
    const model = localStorage.getItem('llmModel') || '';
    const response = await apiClient.post('/draft/generate', {
        objective,
        officer_decisions: officerDecisions,
        language,
        llm_provider: provider,
        llm_model: model
    });
    return response.data;
};

export const checkLegalCompliance = async (grJson) => {
    const response = await apiClient.post('/draft/legal_review', grJson);
    return response.data;
};

export const translateDraft = async (text, targetLanguage) => {
  const response = await apiClient.post('/draft/translate', {
    text: text,
    target_language: targetLanguage,
    llm_provider: 'groq'
  });
  return response.data;
};

export const askFAQ = async (question) => {
    const provider = localStorage.getItem('llmProvider') || 'groq';
    const model = localStorage.getItem('llmModel') || '';
    const response = await apiClient.post('/faq/ask', { question, llm_provider: provider, llm_model: model });
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
