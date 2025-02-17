// server.js
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const port = 3000;

// Middleware to parse incoming request bodies
app.use(bodyParser.json());

let users = []; // This will be a mock database for this example

// Register Endpoint
app.post('/register', async (req, res) => {
    const { username, password } = req.body;

    // Check if user already exists
    const existingUser = users.find(user => user.username === username);
    if (existingUser) {
        return res.status(400).json({ message: 'User already exists' });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Store user in the "database"
    const newUser = { username, password: hashedPassword };
    users.push(newUser);

    res.status(201).json({ message: 'User registered successfully' });
});

// Login Endpoint
app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    // Find user by username
    const user = users.find(user => user.username === username);
    if (!user) {
        return res.status(400).json({ message: 'User not found' });
    }

    // Compare the provided password with the stored hashed password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return res.status(400).json({ message: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign({ username: user.username }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.json({ message: 'Login successful', token });
});

// Middleware to authenticate using JWT token
const authenticateJWT = (req, res, next) => {
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
        return res.status(403).json({ message: 'Access denied, token required' });
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ message: 'Invalid token' });
        }
        req.user = user;
        next();
    });
};

// Protected Route Example
app.get('/dashboard', authenticateJWT, (req, res) => {
    res.json({ message: `Welcome to the dashboard, ${req.user.username}!` });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
