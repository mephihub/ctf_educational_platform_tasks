// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the userportal_ctf database
db = db.getSiblingDB('userportal_ctf');

// Create a user for the application
db.createUser({
  user: 'appuser',
  pwd: 'apppassword',
  roles: [
    {
      role: 'readWrite',
      db: 'userportal_ctf'
    }
  ]
});

// Create indexes for better performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });
db.users.createIndex({ "isActive": 1 });
db.users.createIndex({ "profile.department": 1 });

db.flags.createIndex({ "name": 1 }, { unique: true });
db.flags.createIndex({ "isActive": 1 });

print('Database initialization completed successfully!');
