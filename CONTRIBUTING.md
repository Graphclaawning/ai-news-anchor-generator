# Contributing to ai-news-anchor-generator

Thanks for wanting to make the newsroom better. This is a service-oriented
Python codebase — thin handlers, business services, data models, platform
adapters. Read this before you open a PR.

## Repo shape

```
src/ai_news_anchor/
  bootstrap/        # entry points, DI wiring, app lifecycle
  handlers/         # thin request handlers (CLI + HTTP)
  services/         # business logic (the actual newsroom)
  adapters/         # platform adapters (TTS, LLM, storage, capture)
  models/           # pydantic data models
  config/           # settings, presets, personas
  utils/            # cross-cutting helpers
tests/
```

## Ground rules

- **Handlers stay thin.** A handler parses input, calls one service, returns.
  If a handler has an `if` chain longer than three branches, the logic belongs
  in a service.
- **Adapters own the outside world.** No service imports `openai`, `torch`,
  `requests`, or a filesystem library directly. It goes through an adapter
  protocol. This is what makes the anchor testable without a GPU.
- **Models are frozen.** Data models are immutable pydantic v2 models. If you
  need a variant, make a new one.
- **Type everything.** `mypy --strict` on `src/`. No `Any` unless you justify
  it in a comment on the same line.

## Adding a new anchor persona

1. Drop a YAML file in `config/personas/`.
2. Add a matching voice profile under `anchors/voices/` (see `VOICE_FORMAT.md`
   if we've shipped one — otherwise ask in the issue).
3. Run `python -m ai_news_anchor.bootstrap.cli personas validate`.
4. Open the PR. Include a 20-second sample render in the description.

## Adding a new TTS backend

Implement the `TtsAdapter` protocol in `adapters/tts/`. Register it in
`adapters/tts/registry.py`. Add a test that renders a fixed 12-word script
and asserts the waveform length is within ±5% of the reference backend.

## Testing

```bash
pip install -e ".[dev]"
pytest -q
ruff check src tests
mypy src
```

CI runs all three on Windows-latest and Ubuntu-latest. PRs that break
`mypy --strict` will not be merged.

## Commit style

Conventional commits. `feat(tts):`, `fix(segmenter):`, `chore(deps):`. Scope
is the subpackage, not the file.

## Code of conduct

Be normal. We're building a fake news anchor. It's not that serious.