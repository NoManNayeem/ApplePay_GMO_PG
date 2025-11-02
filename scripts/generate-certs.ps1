# PowerShell script to generate self-signed SSL certificates for Windows

$certDir = ".\certs"
if (-not (Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir | Out-Null
}

Write-Host "Generating self-signed SSL certificates for development..." -ForegroundColor Green

# Check if OpenSSL is available
try {
    $opensslVersion = openssl version
    Write-Host "OpenSSL found: $opensslVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ OpenSSL not found. Please install OpenSSL:" -ForegroundColor Red
    Write-Host "   Option 1: Install via Chocolatey: choco install openssl" -ForegroundColor Yellow
    Write-Host "   Option 2: Download from https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "   Option 3: Use WSL/Linux subsystem" -ForegroundColor Yellow
    exit 1
}

# Generate private key
openssl genrsa -out "$certDir\server.key" 2048

# Generate certificate
$certConfig = @"
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = v3_req

[ req_distinguished_name ]

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
"@

$configFile = "$certDir\openssl.conf"
$certConfig | Out-File -FilePath $configFile -Encoding ASCII

openssl req -new -x509 -key "$certDir\server.key" -out "$certDir\server.crt" `
    -days 365 -config $configFile `
    -subj "/C=US/ST=Development/L=Local/O=ApplePayPOC/OU=Dev/CN=localhost"

Remove-Item $configFile

Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
Write-Host "   Certificate: $certDir\server.crt" -ForegroundColor Cyan
Write-Host "   Private Key: $certDir\server.key" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Note: This is a self-signed certificate for development only." -ForegroundColor Yellow
Write-Host "   You will need to accept the security warning in your browser." -ForegroundColor Yellow

