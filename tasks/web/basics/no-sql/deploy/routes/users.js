const express = require('express');
const User = require('../models/User');
const { authenticateToken, requirePermission } = require('../middleware/auth');

const router = express.Router();

// Get all users (requires read permission)
router.get('/', authenticateToken, requirePermission('read'), async (req, res) => {
  try {
    const { search, department, role, page = 1, limit = 10 } = req.query;
    
    let query = { isActive: true };
    
    // Add search filters
    if (search) {
      query.$or = [
        { username: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
        { 'profile.firstName': { $regex: search, $options: 'i' } },
        { 'profile.lastName': { $regex: search, $options: 'i' } }
      ];
    }
    
    if (department) {
      query['profile.department'] = department;
    }
    
    if (role) {
      query.role = role;
    }

    const skip = (page - 1) * limit;
    const users = await User.find(query)
      .select('-password')
      .skip(skip)
      .limit(parseInt(limit))
      .sort({ createdAt: -1 });

    const total = await User.countDocuments(query);

    res.json({
      users,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user by ID
router.get('/:id', authenticateToken, requirePermission('read'), async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user profile
router.put('/:id', authenticateToken, requirePermission('write'), async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    // Users can only update their own profile unless they have admin role
    if (req.user._id.toString() !== id && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Can only update your own profile' });
    }

    // Don't allow updating sensitive fields
    delete updates.password;
    delete updates.role;
    delete updates.permissions;
    delete updates._id;

    const user = await User.findByIdAndUpdate(
      id,
      { $set: updates },
      { new: true, runValidators: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete user (soft delete)
router.delete('/:id', authenticateToken, requirePermission('delete'), async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { isActive: false },
      { new: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ message: 'User deactivated successfully', user });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user statistics
router.get('/stats/overview', authenticateToken, requirePermission('read'), async (req, res) => {
  try {
    const totalUsers = await User.countDocuments({ isActive: true });
    const activeUsers = await User.countDocuments({ 
      isActive: true, 
      lastLogin: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } 
    });
    
    const usersByRole = await User.aggregate([
      { $match: { isActive: true } },
      { $group: { _id: '$role', count: { $sum: 1 } } }
    ]);

    const usersByDepartment = await User.aggregate([
      { $match: { isActive: true } },
      { $group: { _id: '$profile.department', count: { $sum: 1 } } }
    ]);

    res.json({
      totalUsers,
      activeUsers,
      usersByRole,
      usersByDepartment
    });
  } catch (error) {
    console.error('Error fetching user stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
