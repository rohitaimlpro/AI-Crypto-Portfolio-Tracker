// js/portfolio.js
import { API_ENDPOINTS } from './config.js';
import { apiCall, isAuthenticated, removeTokens } from './api.js';

// Check authentication
if (!isAuthenticated()) {
    window.location.href = 'index.html';
}

let portfolioId = null;
let portfolio = null;
let holdings = [];

// Get portfolio ID from URL
const urlParams = new URLSearchParams(window.location.search);
portfolioId = urlParams.get('id');

if (!portfolioId) {
    window.location.href = 'dashboard.html';
}

// Initialize
async function init() {
    try {
        await loadUserInfo();
        await loadPortfolio();
        await loadHoldings();
        setupEventListeners();
    } catch (error) {
        console.error('Initialization error:', error);
        if (error.message.includes('401')) {
            removeTokens();
            window.location.href = 'index.html';
        }
    }
}

// Load user info
async function loadUserInfo() {
    try {
        const user = await apiCall(API_ENDPOINTS.ME);
        document.getElementById('userInfo').innerHTML = `
            <strong>${user.username}</strong><br>
            <small>${user.email}</small>
        `;
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Load portfolio details
async function loadPortfolio() {
    try {
        portfolio = await apiCall(API_ENDPOINTS.PORTFOLIO_BY_ID(portfolioId));
        
        document.getElementById('portfolioName').textContent = portfolio.name;
        document.getElementById('portfolioDescription').textContent = portfolio.description || 'No description';
        
    } catch (error) {
        console.error('Error loading portfolio:', error);
        alert('Portfolio not found');
        window.location.href = 'dashboard.html';
    }
}

// Load holdings and valuation
async function loadHoldings() {
    try {
        // Load holdings
        const holdingsData = await apiCall(API_ENDPOINTS.PORTFOLIO_HOLDINGS(portfolioId));
        holdings = holdingsData.holdings || [];
        
        // Load valuation
        const valuation = await apiCall(API_ENDPOINTS.PORTFOLIO_VALUATION(portfolioId));
        
        // Update stats
        updatePortfolioStats(valuation);
        
        // Render holdings
        renderHoldings(valuation.holdings || []);
        
    } catch (error) {
        console.error('Error loading holdings:', error);
        document.getElementById('holdingsContainer').innerHTML = `
            <div class="loading" style="color: var(--danger-color);">
                Failed to load holdings
            </div>
        `;
    }
}

// Update portfolio statistics
function updatePortfolioStats(valuation) {
    const totalValue = valuation.total_value_usd || 0;
    const holdingsCount = valuation.holdings?.length || 0;
    
    let totalProfitLoss = 0;
    valuation.holdings?.forEach(h => {
        if (h.profit_loss) {
            totalProfitLoss += h.profit_loss;
        }
    });
    
    document.getElementById('totalValue').textContent = `$${totalValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
    
    document.getElementById('totalCoins').textContent = holdingsCount;
    
    const profitLossEl = document.getElementById('totalProfitLoss');
    profitLossEl.textContent = `$${Math.abs(totalProfitLoss).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
    profitLossEl.className = `value ${totalProfitLoss >= 0 ? 'positive' : 'negative'}`;
}

// Render holdings table
function renderHoldings(valuationHoldings) {
    const container = document.getElementById('holdingsContainer');
    
    if (valuationHoldings.length === 0) {
        container.innerHTML = `
            <div class="loading">
                No coins in this portfolio yet. Click "Add Coin" to get started!
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="holdings-table">
            <table>
                <thead>
                    <tr>
                        <th>Coin</th>
                        <th>Current Price</th>
                        <th>Quantity</th>
                        <th>Holdings Value</th>
                        <th>Avg Buy Price</th>
                        <th>Profit/Loss</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${valuationHoldings.map(holding => `
                        <tr>
                            <td>
                                <div class="coin-info">
                                    <div>
                                        <div class="coin-symbol">${holding.symbol}</div>
                                        <div class="coin-name">${holding.coin_id}</div>
                                    </div>
                                </div>
                            </td>
                            <td>$${holding.current_price.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            })}</td>
                            <td>${holding.quantity.toLocaleString('en-US', {
                                minimumFractionDigits: 8,
                                maximumFractionDigits: 8
                            })}</td>
                            <td>$${holding.holding_value.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            })}</td>
                            <td>${holding.average_buy_price ? '$' + holding.average_buy_price.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }) : '-'}</td>
                            <td class="${holding.profit_loss >= 0 ? 'positive' : 'negative'}">
                                ${holding.profit_loss ? '$' + Math.abs(holding.profit_loss).toLocaleString('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                }) : '-'}
                            </td>
                            <td>
                                <button class="btn-ai" onclick="showAIInsights('${holding.coin_id}')">
                                    AI Insights
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Setup event listeners
function setupEventListeners() {
    // Add coin button
    document.getElementById('addCoinBtn').addEventListener('click', () => {
        document.getElementById('addCoinModal').classList.remove('hidden');
    });
    
    // Close modals
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('addCoinModal').classList.add('hidden');
        });
    });
    
    document.querySelector('.close-modal-insights')?.addEventListener('click', () => {
        document.getElementById('aiInsightsModal').classList.add('hidden');
    });
    
    // Coin search
    let searchTimeout;
    document.getElementById('coinSearch').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            document.getElementById('coinSearchResults').classList.remove('show');
            return;
        }
        
        searchTimeout = setTimeout(() => searchCoins(query), 300);
    });
    
    // Add coin form
    document.getElementById('addCoinForm').addEventListener('submit', handleAddCoin);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        removeTokens();
        window.location.href = 'index.html';
    });
}

// Search coins
async function searchCoins(query) {
    try {
        const data = await apiCall(`${API_ENDPOINTS.COIN_SEARCH}?query=${encodeURIComponent(query)}`);
        const results = data.results || [];
        
        const resultsContainer = document.getElementById('coinSearchResults');
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div style="padding: 12px; color: var(--text-secondary);">No coins found</div>';
        } else {
            resultsContainer.innerHTML = results.map(coin => `
                <div class="search-result-item" onclick="selectCoin('${coin.id}', '${coin.symbol}', '${coin.name}')">
                    <div class="search-result-info">
                        <div class="search-result-name">${coin.name}</div>
                        <div class="search-result-symbol">${coin.symbol}</div>
                    </div>
                </div>
            `).join('');
        }
        
        resultsContainer.classList.add('show');
        
    } catch (error) {
        console.error('Error searching coins:', error);
    }
}

// Select coin from search
window.selectCoin = function(coinId, symbol, name) {
    document.getElementById('coinId').value = coinId;
    document.getElementById('coinSymbol').value = symbol.toUpperCase();
    document.getElementById('coinSearch').value = name;
    document.getElementById('coinSearchResults').classList.remove('show');
}

// Handle add coin
async function handleAddCoin(e) {
    e.preventDefault();
    
    const coinId = document.getElementById('coinId').value;
    const symbol = document.getElementById('coinSymbol').value;
    const quantity = parseFloat(document.getElementById('quantity').value);
    const buyPrice = document.getElementById('buyPrice').value;
    
    try {
        await apiCall(API_ENDPOINTS.PORTFOLIO_HOLDINGS(portfolioId), {
            method: 'POST',
            body: JSON.stringify({
                coin_id: coinId,
                symbol: symbol,
                quantity: quantity,
                average_buy_price: buyPrice ? parseFloat(buyPrice) : null
            })
        });
        
        // Close modal and reload
        document.getElementById('addCoinModal').classList.add('hidden');
        document.getElementById('addCoinForm').reset();
        document.getElementById('coinSearchResults').classList.remove('show');
        
        await loadHoldings();
        
    } catch (error) {
        alert('Failed to add coin: ' + error.message);
    }
}

// Show AI insights
window.showAIInsights = async function(coinId) {
    const modal = document.getElementById('aiInsightsModal');
    modal.classList.remove('hidden');
    
    document.getElementById('insightCoinName').textContent = coinId;
    document.getElementById('aiInsightsContent').innerHTML = '<div class="loading">Generating AI insights...</div>';
    
    try {
        const insights = await apiCall(API_ENDPOINTS.AI_INSIGHTS(coinId));
        
        renderAIInsights(insights);
        
    } catch (error) {
        document.getElementById('aiInsightsContent').innerHTML = `
            <div class="loading" style="color: var(--danger-color);">
                Failed to load AI insights: ${error.message}
            </div>
        `;
    }
}

// Render AI insights
function renderAIInsights(insights) {
    const content = `
        <div class="insight-summary">
            <span class="insight-sentiment sentiment-${insights.sentiment}">
                ${insights.sentiment.toUpperCase()}
            </span>
            <p>${insights.summary}</p>
        </div>
        
        <div class="key-points">
            <h4>Key Points:</h4>
            <ul>
                ${insights.key_points.map(point => `<li>${point}</li>`).join('')}
            </ul>
        </div>
        
        <div class="recommendation-box">
            <h4>Recommendation: ${insights.recommendation.toUpperCase()}</h4>
            <p>Risk Level: <strong>${insights.risk_level.toUpperCase()}</strong></p>
            ${insights.news_sources ? `<p style="margin-top: 8px; font-size: 13px; color: var(--text-secondary);">Based on ${insights.news_sources} recent news sources</p>` : ''}
        </div>
    `;
    
    document.getElementById('aiInsightsContent').innerHTML = content;
}

// Initialize
init();