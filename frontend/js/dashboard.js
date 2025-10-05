// js/dashboard.js
import { API_ENDPOINTS } from './config.js';
import { apiCall, isAuthenticated, removeTokens } from './api.js';

// Check authentication
if (!isAuthenticated()) {
    window.location.href = 'index.html';
}

let portfolios = [];
let currentUser = null;

// Initialize dashboard
async function init() {
    try {
        await loadUserInfo();
        await loadPortfolios();
        setupEventListeners();
    } catch (error) {
        console.error('Initialization error:', error);
        if (error.message.includes('401')) {
            removeTokens();
            window.location.href = 'index.html';
        }
    }
}

// Load user information
async function loadUserInfo() {
    try {
        currentUser = await apiCall(API_ENDPOINTS.ME);
        document.getElementById('userInfo').innerHTML = `
            <strong>${currentUser.username}</strong><br>
            <small>${currentUser.email}</small>
        `;
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Load portfolios
async function loadPortfolios() {
    try {
        portfolios = await apiCall(API_ENDPOINTS.PORTFOLIOS);
        
        // Update stats
        updateDashboardStats();
        
        // Render portfolios
        renderPortfolios();
        
    } catch (error) {
        console.error('Error loading portfolios:', error);
        document.getElementById('portfoliosList').innerHTML = `
            <div class="loading" style="color: var(--danger-color);">
                Failed to load portfolios. Please refresh the page.
            </div>
        `;
    }
}

// Update dashboard statistics
function updateDashboardStats() {
    const totalPortfolios = portfolios.length;
    const totalCoins = portfolios.reduce((sum, p) => sum + p.holdings_count, 0);
    
    document.getElementById('portfolioCount').textContent = totalPortfolios;
    document.getElementById('coinCount').textContent = totalCoins;
    document.getElementById('totalValue').textContent = '$0.00'; // Will be updated with valuations
    document.getElementById('totalProfit').textContent = '$0.00';
}

// Render portfolios list
function renderPortfolios() {
    const container = document.getElementById('portfoliosList');
    
    if (portfolios.length === 0) {
        container.innerHTML = `
            <div class="loading">
                No portfolios yet. Create your first portfolio to get started!
            </div>
        `;
        return;
    }
    
    container.innerHTML = portfolios.map(portfolio => `
        <div class="portfolio-card" onclick="viewPortfolio(${portfolio.id})">
            <h3>${escapeHtml(portfolio.name)}</h3>
            <p>${escapeHtml(portfolio.description || 'No description')}</p>
            <div class="portfolio-stats">
                <span>${portfolio.holdings_count} coin${portfolio.holdings_count !== 1 ? 's' : ''}</span>
                <span>${portfolio.is_public ? '🌍 Public' : '🔒 Private'}</span>
            </div>
            <div class="portfolio-value" id="portfolio-value-${portfolio.id}">
                Loading...
            </div>
        </div>
    `).join('');
    
    // Load valuations for each portfolio
    portfolios.forEach(portfolio => loadPortfolioValuation(portfolio.id));
}

// Load portfolio valuation
async function loadPortfolioValuation(portfolioId) {
    try {
        const valuation = await apiCall(API_ENDPOINTS.PORTFOLIO_VALUATION(portfolioId));
        const valueEl = document.getElementById(`portfolio-value-${portfolioId}`);
        
        if (valueEl) {
            const value = valuation.total_value_usd || 0;
            valueEl.textContent = `$${value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        }
    } catch (error) {
        console.error(`Error loading valuation for portfolio ${portfolioId}:`, error);
        const valueEl = document.getElementById(`portfolio-value-${portfolioId}`);
        if (valueEl) {
            valueEl.textContent = '$0.00';
        }
    }
}

// View portfolio details
window.viewPortfolio = function(portfolioId) {
    window.location.href = `portfolio.html?id=${portfolioId}`;
}

// Setup event listeners
function setupEventListeners() {
    // Create portfolio button
    document.getElementById('createPortfolioBtn').addEventListener('click', () => {
        document.getElementById('createPortfolioModal').classList.remove('hidden');
    });
    
    // Close modal
    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('createPortfolioModal').classList.add('hidden');
    });
    
    // Create portfolio form
    document.getElementById('createPortfolioForm').addEventListener('submit', handleCreatePortfolio);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        removeTokens();
        window.location.href = 'index.html';
    });
}

// Handle create portfolio
async function handleCreatePortfolio(e) {
    e.preventDefault();
    
    const name = document.getElementById('portfolioName').value;
    const description = document.getElementById('portfolioDescription').value;
    const isPublic = document.getElementById('portfolioPublic').checked;
    
    try {
        await apiCall(API_ENDPOINTS.PORTFOLIOS, {
            method: 'POST',
            body: JSON.stringify({
                name,
                description: description || null,
                is_public: isPublic
            })
        });
        
        // Close modal and reload portfolios
        document.getElementById('createPortfolioModal').classList.add('hidden');
        document.getElementById('createPortfolioForm').reset();
        
        await loadPortfolios();
        
    } catch (error) {
        alert('Failed to create portfolio: ' + error.message);
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
init();