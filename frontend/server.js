const { createServer } = require('https');
const { parse } = require('url');
const next = require('next');
const fs = require('fs');
const path = require('path');

const dev = process.env.NODE_ENV !== 'production';
const hostname = '0.0.0.0'; // Listen on all interfaces
const port = parseInt(process.env.PORT || '3443', 10); // HTTPS port

// Disable Turbopack to avoid internal errors - use webpack instead
// Turbopack is enabled by default in Next.js 16, but has stability issues
// We disable it explicitly in the config and ensure webpack is used
const app = next({ 
  dev,
  // Note: turbo option is not directly supported in next() constructor
  // Disable via environment variable instead
});

const handle = app.getRequestHandler();

// Path to SSL certificates
const certPath = process.env.SSL_CERT_PATH || '/certs/server.crt';
const keyPath = process.env.SSL_KEY_PATH || '/certs/server.key';

app.prepare().then(() => {
  // Try to load SSL certificates
  let httpsOptions = null;
  
  try {
    if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
      httpsOptions = {
        key: fs.readFileSync(keyPath),
        cert: fs.readFileSync(certPath),
      };
      console.log('✅ SSL certificates loaded. Starting HTTPS server...');
    } else {
      console.error('❌ SSL certificates not found!');
      console.error(`   Looking for certs at: ${certPath} and ${keyPath}`);
      console.error('   Please ensure certificates are generated.');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Error loading SSL certificates:', error.message);
    process.exit(1);
  }

  if (!httpsOptions) {
    console.error('❌ HTTPS options not available. Cannot start server.');
    process.exit(1);
  }

  // Create HTTPS server
  const server = createServer(httpsOptions, async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true);
      await handle(req, res, parsedUrl);
    } catch (err) {
      console.error('Error occurred handling', req.url, err);
      res.statusCode = 500;
      res.end('internal server error');
    }
  });

  server.listen(port, hostname, (err) => {
    if (err) {
      console.error('❌ Failed to start HTTPS server:', err);
      process.exit(1);
    }
    console.log(`✅ Ready on https://${hostname}:${port}`);
    console.log(`   Access at: https://localhost:${port}`);
    console.log(`   Also try: https://127.0.0.1:${port}`);
    console.log(`   Note: Browser will show security warning for self-signed certificate`);
    console.log(`   Click "Advanced" → "Proceed to localhost (unsafe)" to continue`);
  });

  // Also start HTTP server on port 3000 as fallback (for testing, but won't work with Apple Pay)
  const http = require('http');
  const httpServer = http.createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true);
      await handle(req, res, parsedUrl);
    } catch (err) {
      console.error('Error occurred handling', req.url, err);
      res.statusCode = 500;
      res.end('internal server error');
    }
  });

  httpServer.listen(3000, hostname, (err) => {
    if (err) {
      console.error('⚠️  Failed to start HTTP fallback server:', err);
    } else {
      console.log(`⚠️  HTTP fallback server on http://localhost:3000 (Apple Pay won't work on HTTP)`);
    }
  });

  // Handle graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing HTTPS server');
    server.close(() => {
      console.log('HTTPS server closed');
      process.exit(0);
    });
  });
}).catch((err) => {
  console.error('❌ Failed to prepare Next.js app:', err);
  process.exit(1);
});

