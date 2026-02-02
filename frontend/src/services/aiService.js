import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const API_URL = `${BASE_URL}/ai`;

const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return { headers: { Authorization: `Bearer ${token}` } };
};

const aiService = {
    chat: async (message, context = "") => {
        const response = await axios.post(`${API_URL}/chat`, { message, context }, getAuthHeader());
        return response.data;
    }
};

export default aiService;
