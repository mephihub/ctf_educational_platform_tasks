const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const config = require('../config');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Login endpoint - VULNERABLE to NoSQL injection
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    // VULNERABILITY: Direct use of user input in MongoDB query
    // This allows NoSQL injection attacks
    const user = await User.findOne({ 
      username: username,
      password: password // This should be hashed comparison!
    });

    if (!user) {
      // Try with password comparison for legitimate users
      const userByUsername = await User.findOne({ username: username });
      if (userByUsername && await userByUsername.comparePassword(password)) {
        const token = jwt.sign(
          { userId: userByUsername._id, username: userByUsername.username },
          config.JWT_SECRET,
          { expiresIn: '24h' }
        );

        // Update last login
        userByUsername.lastLogin = new Date();
        await userByUsername.save();

        return res.json({
          success: true,
          token,
          user: userByUsername
        });
      }
      
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // If found by direct query (vulnerable path)
    const token = jwt.sign(
      { userId: user._id, username: user.username },
      config.JWT_SECRET,
      { expiresIn: '24h' }
    );

    // Update last login
    user.lastLogin = new Date();
    await user.save();

    res.json({
      success: true,
      token,
      user: user
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Register endpoint
router.post('/register', async (req, res) => {
  try {
    const { username, email, password, firstName, lastName } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }

    // Check if user already exists
    const existingUser = await User.findOne({
      $or: [{ username }, { email }]
    });

    if (existingUser) {
      return res.status(400).json({ error: 'Username or email already exists' });
    }

    // Create new user
    const user = new User({
      username,
      email,
      password,
      profile: {
        firstName: firstName || '',
        lastName: lastName || ''
      },
      permissions: ['read']
    });

    await user.save();

    const token = jwt.sign(
      { userId: user._id, username: user.username },
      config.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      success: true,
      token,
      user: user
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get current user
router.get('/me', authenticateToken, (req, res) => {
  res.json({ user: req.user });
});

// Logout (client-side token removal)
router.post('/logout', authenticateToken, (req, res) => {
  res.json({ success: true, message: 'Logged out successfully' });
});

module.exports = router;
