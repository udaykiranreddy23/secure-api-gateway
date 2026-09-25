# Secure API Gateway

Security-focused gateway demonstrating JWT authentication, API-key authentication, RBAC, Redis rate limiting, request IDs, audit logging, security headers and reverse proxying.

## Architecture

```text
Client
  |
  v
Gateway
  |- Authentication
  |- RBAC
  |- Rate Limiting
  |- Audit Logging
  `- Request ID
  |
  v
Upstream API
```

## Run

```bash
docker compose up --build
```

Gateway: http://localhost:8080/docs

Get a development token:

```bash
curl -X POST http://localhost:8080/auth/token   -H "Content-Type: application/json"   -d '{"username":"admin","password":"admin123"}'
```

Then:

```bash
curl http://localhost:8080/proxy/orders   -H "Authorization: Bearer <TOKEN>"
```

Local demo API key: `demo-service-key`

## Security note

Demo credentials and the default JWT secret are for local development only. Production deployments should use a secret manager, TLS, strong credential storage, key rotation and a reviewed threat model.
