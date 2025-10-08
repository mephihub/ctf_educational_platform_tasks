const mongoose = require('mongoose');
const User = require('../models/User');
const Flag = require('../models/Flag');
const config = require('../config');

const seedData = async () => {
  try {
    await mongoose.connect(config.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log('Connected to MongoDB');

    // Clear existing data
    await User.deleteMany({});
    await Flag.deleteMany({});

    // Create test users
    const users = [
      {
        username: 'admin',
        email: 'admin@userportal.com',
        password: 'admin123',
        role: 'admin',
        profile: {
          firstName: 'System',
          lastName: 'Administrator',
          department: 'IT',
          position: 'System Admin',
          phone: '+1-555-0001'
        },
        permissions: ['read', 'write', 'delete', 'admin', 'flag_access']
      },
      {
        username: 'jdoe',
        email: 'john.doe@userportal.com',
        password: 'password123',
        role: 'user',
        profile: {
          firstName: 'John',
          lastName: 'Doe',
          department: 'Engineering',
          position: 'Software Developer',
          phone: '+1-555-0002'
        },
        permissions: ['read', 'write']
      },
      {
        username: 'msmith',
        email: 'mary.smith@userportal.com',
        password: 'secure456',
        role: 'moderator',
        profile: {
          firstName: 'Mary',
          lastName: 'Smith',
          department: 'HR',
          position: 'HR Manager',
          phone: '+1-555-0003'
        },
        permissions: ['read', 'write', 'delete']
      },
      {
        username: 'bwilson',
        email: 'bob.wilson@userportal.com',
        password: 'mypass789',
        role: 'user',
        profile: {
          firstName: 'Bob',
          lastName: 'Wilson',
          department: 'Marketing',
          position: 'Marketing Specialist',
          phone: '+1-555-0004'
        },
        permissions: ['read']
      },
      {
        username: 'ajohnson',
        email: 'alice.johnson@userportal.com',
        password: 'alice2024',
        role: 'user',
        profile: {
          firstName: 'Alice',
          lastName: 'Johnson',
          department: 'Finance',
          position: 'Financial Analyst',
          phone: '+1-555-0005'
        },
        permissions: ['read', 'write']
      },
      {
        username: 'ctaylor',
        email: 'chris.taylor@userportal.com',
        password: 'chris123',
        role: 'user',
        profile: {
          firstName: 'Chris',
          lastName: 'Taylor',
          department: 'Engineering',
          position: 'DevOps Engineer',
          phone: '+1-555-0006'
        },
        permissions: ['read', 'write']
      },
      {
        username: 'sgarcia',
        email: 'sarah.garcia@userportal.com',
        password: 'sarah456',
        role: 'user',
        profile: {
          firstName: 'Sarah',
          lastName: 'Garcia',
          department: 'Design',
          position: 'UX Designer',
          phone: '+1-555-0007'
        },
        permissions: ['read']
      },
      {
        username: 'dlee',
        email: 'david.lee@userportal.com',
        password: 'david789',
        role: 'user',
        profile: {
          firstName: 'David',
          lastName: 'Lee',
          department: 'Sales',
          position: 'Sales Representative',
          phone: '+1-555-0008'
        },
        permissions: ['read']
      }
    ];

    // Create users
    for (const userData of users) {
      const user = new User(userData);
      await user.save();
      console.log(`Created user: ${user.username}`);
    }

    // Create flag
    const flag = new Flag({
      name: 'nosql_injection_flag',
      value: 'CTF{n0sql_1nj3ct10n_m4st3r}',
      description: 'Flag for NoSQL Injection challenge',
      category: 'web',
      points: 150
    });

    await flag.save();
    console.log('Created flag');

    console.log('Database seeded successfully!');
    console.log('\\nTest credentials:');
    console.log('Admin: admin / admin123');
    console.log('User: jdoe / password123');
    console.log('Moderator: msmith / secure456');
    
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    await mongoose.connection.close();
  }
};

seedData();
