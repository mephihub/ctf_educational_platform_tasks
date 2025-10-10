const mongoose = require('mongoose');

const flagSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  value: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    enum: ['web', 'crypto', 'pwn', 'reverse', 'misc'],
    default: 'web'
  },
  points: {
    type: Number,
    default: 100
  },
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Flag', flagSchema);
