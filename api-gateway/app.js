const express = require('express');
const app = express();
const port = 3000;

// Basic route to check if the API Gateway is running
app.get('/status', (req, res) => {
    res.json({ message: 'API Gateway is running!' });
});

// Start the server
app.listen(port, () => {
    console.log(`API Gateway running on http://localhost:${port}`);
});
