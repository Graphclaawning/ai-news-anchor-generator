# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@ai-news-anchor-generator.invalid` with:

- A description of the issue.
- Reproduction steps (a minimal script is ideal).
- The version string from `ai-news-anchor --version`.
- Whether the issue requires a crafted feed URL, a crafted persona YAML, or
  local filesystem access.

We aim to acknowledge within 72 hours and to publish a fix or mitigation
within 30 days for confirmed issues.

## Threat model

`ai-news-anchor-generator` ingests untrusted content: RSS feeds, scraped
article bodies, and user-supplied persona YAML. The following are in scope:

- **YAML deserialization.** Persona files are parsed with `yaml.safe_load`.
  Any PR that swaps this for `yaml.load` will be rejected.
- **Feed parsing.** RSS/Atom bodies are treated as hostile. The parser
  strips script tags, refuses `file://` and `data:` URLs, and enforces a
  2 MB per-item cap before handing text to the LLM adapter.
- **Path traversal in voice profiles.** Voice profile names are validated
  against `^[a-z0-9_-]{1,32}$` before being joined to `anchors/voices/`.
- **Prompt injection via article bodies.** Article text is fenced and
  labelled as untrusted in every prompt. The LLM adapter strips any
  instruction that tries to reassign the system role. See
  `services/script_writer.py` for the fencing logic.
- **Supply chain.** All model weights are pinned by SHA-256 in
  `config/models.lock`. Do not commit unsigned weights.

Out of scope: the fact that the anchor says things. That's the feature.