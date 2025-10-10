const http = require('http');

const options = {
  host: 'localhost',
  port: 3000,
  path: '/api/admin/health',
  timeout: 2000,
  headers: {
    'Authorization': 'Bearer dummy-token-for-healthcheck'
  }
};

const request = http.request(options, (res) => {
  console.log(`Health check status: ${res.statusCode}`);
  if (res.statusCode === 200 || res.statusCode === 401 || res.statusCode === 403) {
    // 401/403 means server is running but auth failed, which is expected
    process.exit(0);
  } else {
    process.exit(1);
  }
});

request.on('error', (err) => {
  console.log('Health check failed:', err.message);
  process.exit(1);
});

request.on('timeout', () => {
  console.log('Health check timeout');
  process.exit(1);
});

request.end();
