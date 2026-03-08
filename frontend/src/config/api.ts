const API_BASE_URL = "/api";

export const apiEndpoints = {
    login: `${API_BASE_URL}/auth/login`,
    signup: `${API_BASE_URL}/auth/register`,
    otp_send: `${API_BASE_URL}/auth/send-otp`,
    otp_verify: `${API_BASE_URL}/auth/verify-otp`,
    schemes: `${API_BASE_URL}/schemes`,
    eligibility: `${API_BASE_URL}/evaluate`,
    upload: `${API_BASE_URL}/upload-document`,
    voice_query: `${API_BASE_URL}/voice/query`,
    health: `${API_BASE_URL}/health`,
    system_health: `${API_BASE_URL}/system-health`,
    anonymous_token: `${API_BASE_URL}/auth/anonymous-token`,
};

export default API_BASE_URL;
