import axios from 'axios';
import { BASE_URL, API_PREFIX } from './httpClient';

const API_URL = `${BASE_URL}${API_PREFIX}/ai`;

console.log(`[AI Service] Using API URL: ${API_URL}`);

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
