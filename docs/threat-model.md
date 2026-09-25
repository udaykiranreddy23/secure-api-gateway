# Threat Model

## Assets
- Authentication tokens
- API keys
- Upstream availability
- Audit records

## Threats
- Invalid/expired credentials
- Privilege escalation
- Excessive request volume
- Upstream failure
- Accidental secret exposure

## Mitigations
| Threat | Mitigation |
|---|---|
| Invalid JWT | Signature + expiration validation |
| Privilege escalation | Explicit role dependency |
| Abuse | Redis-backed rate limiting |
| Upstream failure | Timeout + 503 |
| Secret exposure | Environment variables |
| Traceability | Request ID + audit logging |

This is an educational reference and not a complete production security assessment.
