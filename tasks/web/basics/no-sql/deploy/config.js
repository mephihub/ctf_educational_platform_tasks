module.exports = {
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/userportal_ctf',
  JWT_SECRET: process.env.JWT_SECRET || 'super_secret_jwt_key_for_ctf_challenge_2024',
  PORT: process.env.PORT || 3000,
  NODE_ENV: process.env.NODE_ENV || 'development'
};
