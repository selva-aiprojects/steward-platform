import axios from 'axios';

const RAW_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const BASE_URL = RAW_API_URL.replace(/\/$/, '');
const API_URL = RAW_API_URL.includes('/api/v1') ? `${BASE_URL}/ai` : `${BASE_URL}/api/v1/ai`;

const getUserHeaders = () => {
    try {
        const raw = localStorage.getItem('stocksteward_user');
        if (!raw) return {};
        const user = JSON.parse(raw);
        if (!user?.id) return {};
        return {
            'X-User-Id': String(user.id),
            'X-User-Role': user.role || 'TRADER'
        };
    } catch (error) {
        return {};
    }
};

const aiService = {
    chat: async (message, context = "") => {
        const response = await axios.post(
            `${API_URL}/chat`,
            { message, context },
            { headers: { ...getUserHeaders() } }
        );
        return response.data;
    }
};

export default aiService;
