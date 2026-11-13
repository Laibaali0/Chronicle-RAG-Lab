# Threat model and design limits

## Covered by the reference implementation

- Invalid or oversized API request bodies are rejected by typed validation.
- Sources are filtered against package, exact API version, and effective date.
- HTTP read endpoints can require `x-api-key` when `CHRONICLE_API_KEY` is configured.
- In-memory token bucket limits request rate per process.
- Source citation IDs in optional generated responses must match retrieved IDs.
- Retrieved context is labelled as quoted data, not as assistant instructions.
- A small heuristic detector marks suspicious role spoofing and exfiltration language; it cannot guarantee safety.
- Audit logs store a hashed request identifier and selected operational fields, not raw prompts or credentials.

## Not solved

- Prompt injection remains possible with a real generative model. The detector is not comprehensive.
- Citation validity does not establish that a statement is supported by its citation.
- Document ACLs, tenant isolation, data deletion policy, and secret management are not implemented.
- Rate limits are per process; distributed instances would need a shared durable limiter.
- The service should not be exposed directly to the internet without a reverse proxy, TLS, monitoring, and real authentication/authorization.
- The optional OpenAI-compatible provider uses an explicitly configured HTTPS endpoint; send data only to trusted providers and avoid including confidential documentation without approval.

This project is for demonstration, not security certification or high-stakes production use.
