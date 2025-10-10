# UserPortal - CTF Challenge

A modern enterprise user management system with a NoSQL injection vulnerability.

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- MongoDB (running on localhost:27017)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start MongoDB service (if not already running)

3. Seed the database with test data:
```bash
npm run seed
```

4. Start the application:
```bash
npm start
```

5. Open your browser and navigate to `http://localhost:3000`

## Demo Credentials

- **Admin**: `admin` / `admin123`
- **User**: `jdoe` / `password123`
- **Moderator**: `msmith` / `secure456`

## Features

- Modern, responsive web interface
- User authentication and authorization
- Role-based access control
- User management system
- Admin panel with system monitoring
- Real-time statistics and charts

## Technology Stack

- **Backend**: Node.js, Express.js, MongoDB, Mongoose
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Authentication**: JWT tokens
- **Security**: bcrypt password hashing, rate limiting

## Development

For development with auto-reload:
```bash
npm run dev
```

## Architecture

- `server.js` - Main application server
- `models/` - Database models (User, Flag)
- `routes/` - API endpoints (auth, users, admin)
- `middleware/` - Authentication and authorization middleware
- `public/` - Frontend assets (HTML, CSS, JavaScript)
- `scripts/` - Database seeding scripts

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Users
- `GET /api/users` - Get all users (with pagination and filters)
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user profile
- `DELETE /api/users/:id` - Deactivate user
- `GET /api/users/stats/overview` - Get user statistics

### Admin
- `GET /api/admin/dashboard` - Admin dashboard stats
- `PUT /api/admin/users/:id/role` - Update user role
- `GET /api/admin/logs` - System logs
- `GET /api/admin/flags` - Get flags (requires special permission)
- `GET /api/admin/health` - System health check
