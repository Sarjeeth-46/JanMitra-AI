const API_BASE_URL = import.meta.env.VITE_API_URL || "http://13.234.232.177:8000";

export const apiEndpoints = {
    login: `${API_BASE_URL}/api/auth/login`,
    signup: `${API_BASE_URL}/api/auth/register`,
    otp_send: `${API_BASE_URL}/api/auth/send-otp`,
    otp_verify: `${API_BASE_URL}/api/auth/verify-otp`,
    schemes: `${API_BASE_URL}/api/schemes`,
    eligibility: `${API_BASE_URL}/api/evaluate`,
    upload: `${API_BASE_URL}/api/upload-document`,
    voice_query: `${API_BASE_URL}/api/voice/query`,
    health: `${API_BASE_URL}/api/health`,
    system_health: `${API_BASE_URL}/api/system-health`,
    anonymous_token: `${API_BASE_URL}/api/auth/anonymous-token`,
};

export default API_BASE_URL;
