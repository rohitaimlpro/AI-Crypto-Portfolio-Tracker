// js/config.js
const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
    // Auth
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    ME: `${API_BASE_URL}/api/auth/me`,
    
    // Portfolio
    PORTFOLIOS: `${API_BASE_URL}/api/portfolio`,
    PORTFOLIO_BY_ID: (id) => `${API_BASE_URL}/api/portfolio/${id}`,
    PORTFOLIO_HOLDINGS: (id) => `${API_BASE_URL}/api/portfolio/${id}/holdings`,
    PORTFOLIO_VALUATION: (id) => `${API_BASE_URL}/api/portfolio/${id}/valuation`,
    
    // Coins
    COIN_SEARCH: `${API_BASE_URL}/api/coins/search`,
    COIN_PRICE: (id) => `${API_BASE_URL}/api/coins/${id}/price`,
    COIN_DETAILS: (id) => `${API_BASE_URL}/api/coins/${id}/details`,
    
    // AI
    AI_INSIGHTS: (id) => `${API_BASE_URL}/api/ai/${id}`,
    AI_PORTFOLIO: (id) => `${API_BASE_URL}/api/ai/portfolio/${id}`
};

export const TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';