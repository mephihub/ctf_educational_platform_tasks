const express = require('express');
const User = require('../models/User');
const Flag = require('../models/Flag');
const { authenticateToken, requireRole, requirePermission } = require('../middleware/auth');

const router = express.Router();

// Admin dashboard stats
router.get('/dashboard', authenticateToken, requireRole(['admin']), async (req, res) => {
  try {
    const totalUsers = await User.countDocuments();
    const activeUsers = await User.countDocuments({ isActive: true });
    const adminUsers = await User.countDocuments({ role: 'admin' });
    const recentLogins = await User.countDocuments({
      lastLogin: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
    });

    const userGrowth = await User.aggregate([
      {
        $group: {
          _id: {
            year: { $year: '$createdAt' },
            month: { $month: '$createdAt' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } },
      { $limit: 12 }
    ]);

    res.json({
      stats: {
        totalUsers,
        activeUsers,
        adminUsers,
        recentLogins
      },
      userGrowth
    });
  } catch (error) {
    console.error('Error fetching admin dashboard:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Manage user roles and permissions
router.put('/users/:id/role', authenticateToken, requireRole(['admin']), async (req, res) => {
  try {
    const { role, permissions } = req.body;
    
    if (!['user', 'admin', 'moderator'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role' });
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      { 
        role,
        permissions: permissions || []
      },
      { new: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Error updating user role:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// System logs (simulated)
router.get('/logs', authenticateToken, requireRole(['admin']), async (req, res) => {
  try {
    // Simulate system logs
    const logs = [
      {
        timestamp: new Date(),
        level: 'INFO',
        message: 'User login successful',
        user: 'jdoe',
        ip: '192.168.1.100'
      },
      {
        timestamp: new Date(Date.now() - 60000),
        level: 'WARN',
        message: 'Failed login attempt',
        user: 'unknown',
        ip: '10.0.0.1'
      },
      {
        timestamp: new Date(Date.now() - 120000),
        level: 'INFO',
        message: 'User profile updated',
        user: 'msmith',
        ip: '192.168.1.101'
      }
    ];

    res.json({ logs });
  } catch (error) {
    console.error('Error fetching logs:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Flag management - PROTECTED AREA
router.get('/flags', authenticateToken, requirePermission('flag_access'), async (req, res) => {
  try {
    const flags = await Flag.find({ isActive: true });
    res.json({ flags });
  } catch (error) {
    console.error('Error fetching flags:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get specific flag
router.get('/flags/:id', authenticateToken, requirePermission('flag_access'), async (req, res) => {
  try {
    const flag = await Flag.findById(req.params.id);
    
    if (!flag) {
      return res.status(404).json({ error: 'Flag not found' });
    }

    res.json({ flag });
  } catch (error) {
    console.error('Error fetching flag:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// System health check
router.get('/health', authenticateToken, requireRole(['admin']), async (req, res) => {
  try {
    const dbStatus = 'connected'; // Simplified
    const uptime = process.uptime();
    const memoryUsage = process.memoryUsage();

    res.json({
      status: 'healthy',
      database: dbStatus,
      uptime: Math.floor(uptime),
      memory: {
        used: Math.round(memoryUsage.heapUsed / 1024 / 1024),
        total: Math.round(memoryUsage.heapTotal / 1024 / 1024)
      },
      timestamp: new Date()
    });
  } catch (error) {
    console.error('Error checking system health:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
