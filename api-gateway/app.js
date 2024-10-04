const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;
const Timeout = 5000; // Timeout set to 5 seconds (5000 milliseconds)

// Concurrency limit settings
const MAX_CONCURRENT_TASKS = 5; 
let currentTasks = 0;

// Middleware for JSON parsing
app.use(express.json());

// Concurrency Limiter Middleware
function concurrencyLimiter(req, res, next) {
    if (currentTasks >= MAX_CONCURRENT_TASKS) {
        res.status(429).json({ error: 'Too many concurrent requests' });
    } else {
        currentTasks++;
        res.on('finish', () => {
            currentTasks--;
        });
        next();
    }
}

// Apply the concurrency limiter middleware to all routes
app.use(concurrencyLimiter);

// Route to Prediction Endpoint in Stock-Prediction Service
app.get('/api/predict/:symbol', async (req, res) => {
    try {
        const response = await axios.get(`http://localhost:5000/api/predict/${req.params.symbol}`, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'Prediction Service request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Prediction Service error' });
        }
    }
});

// Route to Stock Data History in Stock-Prediction Service
app.get('/api/stocks/history', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5000/api/stocks/history', { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'Stock Data Service request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Stock Data Service error' });
        }
    }
});

// Cache Clear Route for Stock Data Service
app.post('/api/stocks/cache/clear', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5000/api/stocks/cache/clear', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'Cache Clear request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Error clearing stock data cache' });
        }
    }
});

// User Registration in User Management Service
app.post('/api/users/register', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5002/api/users/register', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User registration request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'User registration error' });
        }
    }
});

// User Login in User Management Service
app.post('/api/users/login', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5002/api/users/login', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User login request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'User login error' });
        }
    }
});

// User Profile Retrieval in User Management Service
app.get('/api/users/profile', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5002/api/users/profile', {
            headers: { 'Authorization': req.headers.authorization },
            timeout: Timeout
        });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User profile retrieval request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Error fetching user profile' });
        }
    }
});

// User Profile Update in User Management Service
app.post('/api/users/profile/update', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5002/api/users/profile/update', req.body, {
            headers: { 'Authorization': req.headers.authorization },
            timeout: Timeout
        });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User profile update request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Error updating user profile' });
        }
    }
});

// User Buy Route
app.post('/api/users/buy', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5002/api/users/buy', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User buy request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'User buy request error' });
        }
    }
});

// User Sell Route
app.post('/api/users/sell', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:5002/api/users/sell', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'User sell request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'User sell request error' });
        }
    }
});

// Route to store transaction details in Stock-Prediction Service
app.post('/api/transactions/store', async (req, res) => {
    console.log("Received data at API Gateway:", req.body);
    try {
        const response = await axios.post('http://localhost:5000/api/transactions/store', req.body, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'Transaction storage request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Error storing transaction data' });
        }
    }
});

// New Route to handle /api/stocks/:symbol/details
app.get('/api/stocks/:symbol/details', async (req, res) => {
    const symbol = req.params.symbol;
    try {
        const response = await axios.get(`http://localhost:5000/api/stocks/${symbol}/details`, { timeout: Timeout });
        res.json(response.data);
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            res.status(504).json({ error: 'Stock Data Service request timed out' });
        } else if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ error: 'Error retrieving stock details' });
        }
    }
});

// Status endpoint for Gateway
app.get('/status', (req, res) => {
    res.json({ message: 'API Gateway is running!' });
});

app.listen(port, () => {
    console.log(`API Gateway running on http://localhost:${port}`);
});
