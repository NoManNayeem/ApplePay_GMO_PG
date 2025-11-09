Place Merchant Identity RSA PEM files here.
Generate from p12:
  openssl pkcs12 -in applepay-merchant-identity.p12 -clcerts -nokeys -out merchant-identity-cert.pem
  openssl pkcs12 -in applepay-merchant-identity.p12 -nocerts -out merchant-identity-key.pem -nodes
File perms:
  chmod 600 merchant-identity-*.pem
