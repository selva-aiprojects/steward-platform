import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/tickets';

const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return { headers: { Authorization: `Bearer ${token}` } };
};

const ticketService = {
    createTicket: async (ticketData) => {
        const response = await axios.post(API_URL, ticketData, getAuthHeader());
        return response.data;
    },

    getTickets: async () => {
        const response = await axios.get(API_URL, getAuthHeader());
        return response.data;
    },

    getTicket: async (id) => {
        const response = await axios.get(`${API_URL}/${id}`, getAuthHeader());
        return response.data;
    },

    updateTicketStatus: async (id, status) => {
        const response = await axios.patch(`${API_URL}/${id}`, { status }, getAuthHeader());
        return response.data;
    },

    addMessage: async (id, message) => {
        const response = await axios.post(`${API_URL}/${id}/messages`, { message }, getAuthHeader());
        return response.data;
    }
};

export default ticketService;
