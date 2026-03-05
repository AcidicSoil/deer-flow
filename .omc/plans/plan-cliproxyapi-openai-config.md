# Plan: Add cliproxyapi-capable OpenAI config/docs support

## Requirements Summary
Implement config/documentation updates so DeerFlow users can route OpenAI-compatible model calls through a local cliproxyapi endpoint (`http://127.0.0.1:8317/v1`) using env-based configuration.

Scope is **config/docs only** (no runtime behavior changes).

## Acceptance Criteria (Pass/Fail)
- [ ] `.env.example` contains an `OPENAI_BASE_URL=` example/comment that references `http://127.0.0.1:8317/v1`, plus guidance to pair with `OPENAI_API_KEY` for cliproxyapi.
- [ ] `config.example.yaml` OpenAI model example contains `base_url: $OPENAI_BASE_URL` (active or clearly documented commented variant in the same OpenAI block) and retains env-based `api_key` usage.
- [ ] `README.md` contains one cliproxyapi setup snippet including both `OPENAI_BASE_URL` and `OPENAI_API_KEY`, and shows matching `config.yaml` model entry using `base_url: $OPENAI_BASE_URL`.
- [ ] `backend/docs/CONFIGURATION.md` contains one cliproxyapi/OpenAI-compatible snippet including both `OPENAI_BASE_URL` and `OPENAI_API_KEY` and explicit note that `api_key` is forwarded to the configured OpenAI-compatible endpoint.
- [ ] Diff contains only config/docs template files (no runtime code paths under `backend/src/models/` or `backend/src/agents/`).

## Scope and Non-Goals
### In Scope
- `.env.example` updates
- `config.example.yaml` OpenAI example updates
- `README.md` quick-start/config guidance updates
- `backend/docs/CONFIGURATION.md` provider configuration updates

### Out of Scope
- Runtime fallback/defaulting logic for `OPENAI_BASE_URL`
- Provider abstraction changes
- Request/response transformation logic
- Any behavior changes in model factory, lead agent, or execution middleware

## Codebase Evidence (file anchors)
- OpenAI model example already uses `langchain_openai:ChatOpenAI` + env API key: `config.example.yaml:16-24`.
- OpenAI-compatible `base_url` pattern already exists (Novita example): `config.example.yaml:26-38`.
- Env interpolation supports `$VAR` recursively: `backend/src/config/app_config.py:103-125`.
- Missing provider env vars fail fast (important for docs wording): `backend/src/config/app_config.py:115-119`.
- Model config fields (including extra fields like `base_url`) are forwarded to provider constructor: `backend/src/models/factory.py:27-49`.
- README currently documents `OPENAI_API_KEY` but not local proxy base URL: `README.md:74-83`, `README.md:93-103`.
- `.env.example` currently includes optional `OPENAI_API_KEY` only: `.env.example:10-16`.
- Backend config docs mention OpenAI-compatible `base_url` generally, but no local cliproxyapi setup: `backend/docs/CONFIGURATION.md:28-43`, `backend/docs/CONFIGURATION.md:176-191`.

## RALPLAN-DR (Short Mode)

### Principles
1. Reuse existing architecture; avoid runtime changes when config surface already supports the feature.
2. Keep setup explicit and copy/paste friendly for local users.
3. Preserve secure secret-handling patterns (env vars, no hardcoded keys).
4. Keep examples consistent across `.env.example`, `config.example.yaml`, and docs.
5. Avoid forcing optional env vars in baseline setups where not needed.

### Decision Drivers (Top 3)
1. Deliver cliproxyapi compatibility with minimal regression risk.
2. Avoid changes to model runtime behavior.
3. Reduce user misconfiguration through explicit and environment-aware examples.

### Viable Options

#### Option A — Config + docs updates only (**favored**)
- Update `.env.example`, `config.example.yaml`, README, and backend docs.
- Keep runtime unchanged.

#### Option B — Runtime fallback default for `OPENAI_BASE_URL` (out of scope)
- Add code fallback in runtime when `base_url` omitted.

#### Option C — Docs-first optionality pattern (in-scope variant)
- Keep runtime unchanged.
- Keep OpenAI baseline working without requiring `OPENAI_BASE_URL` by default; add cliproxy-specific block/snippet with explicit opt-in `OPENAI_BASE_URL`.

### Option Comparison
| Option | Regression Risk | Misconfiguration Risk | Effort | Maintenance Burden | Driver Fit |
|---|---|---|---|---|---|
| A | Low | Medium | Low | Low | Strong |
| B | Medium/High | Low/Medium | Medium | Medium | Weak (violates no-runtime-change driver) |
| C | Low | Low | Low/Medium | Medium | **Strongest** |

### Option Decision
Choose **Option C (A with explicit optionality pattern)**:
- It preserves the favored architecture (config/docs-only, no runtime changes).
- It addresses the strongest counterargument by reducing fail-fast and environment confusion.
- It keeps cliproxyapi setup explicit without breaking non-proxy default onboarding.

## Implementation Steps
1. **Update env template (`.env.example`)**
   - Add optional `OPENAI_BASE_URL=http://127.0.0.1:8317/v1` guidance line (commented example style consistent with file).
   - Add paired guidance that `OPENAI_API_KEY` should hold the credential expected by cliproxyapi.

2. **Update model config example (`config.example.yaml`)**
   - Keep existing baseline OpenAI example with `api_key: $OPENAI_API_KEY`.
   - Add `base_url: $OPENAI_BASE_URL` in a way that is explicitly optional-safe (commented or separate cliproxy example block) to avoid making unset env vars mandatory for baseline users.

3. **Update root README (`README.md`)**
   - In quick-start config sections, add cliproxyapi snippet containing:
     - `OPENAI_BASE_URL=http://127.0.0.1:8317/v1`
     - `OPENAI_API_KEY=<cliproxyapi-key>`
     - matching `config.yaml` model entry with `base_url: $OPENAI_BASE_URL`.
   - Add one sentence clarifying local vs container endpoint note (for Docker, `127.0.0.1` may need host/service address).

4. **Update backend config guide (`backend/docs/CONFIGURATION.md`)**
   - Extend OpenAI-compatible gateway examples with a local cliproxyapi example and explicit API key forwarding semantics.
   - Include concise deployment-context note:
     - local backend process: `http://127.0.0.1:8317/v1`
     - containerized backend: use host/service-resolvable address.

5. **No runtime modifications**
   - Do not edit runtime code under `backend/src/models/`, `backend/src/agents/`, or middleware paths.

## Risks and Mitigations
| Risk | Mitigation Action | Where Applied | Validation |
|---|---|---|---|
| Referencing `$OPENAI_BASE_URL` as required causes startup failure when unset | Make proxy base URL opt-in in examples (commented/cliproxy block), keep baseline non-proxy path intact | `config.example.yaml`, `README.md`, `backend/docs/CONFIGURATION.md` | Verify baseline snippet has no mandatory `OPENAI_BASE_URL`; grep/doc review confirms optional framing |
| `127.0.0.1` misuse under Docker causes connection failures | Add local-vs-container endpoint note | `README.md`, `backend/docs/CONFIGURATION.md` | Verify docs include container note adjacent to cliproxy snippet |
| Ambiguity on which key is used at proxy | Explicitly document key routing: `api_key` is sent to configured OpenAI-compatible endpoint | `README.md`, `backend/docs/CONFIGURATION.md`, `.env.example` comment | Verify exact wording exists in both docs files |
| Naming drift across files | Standardize on `OPENAI_BASE_URL` | all edited docs/config templates | Grep for `OPENAI_BASE_URL` + manual snippet cross-check |

## Verification Steps (Concrete)
1. **Diff file gate**
   - Run: `git diff --name-only`
   - Expected: only `.env.example`, `config.example.yaml`, `README.md`, `backend/docs/CONFIGURATION.md` (or subset) changed.
   - Fail condition: any runtime file under `backend/src/` appears.

2. **Pattern consistency checks**
   - Run checks for these strings in intended files:
     - `OPENAI_BASE_URL`
     - `http://127.0.0.1:8317/v1`
     - `OPENAI_API_KEY`
     - `base_url: $OPENAI_BASE_URL`
   - Expected: present in docs/config templates per acceptance criteria, absent from runtime python files.

3. **Snippet coherence review**
   - Confirm README and CONFIGURATION snippets both include env + model YAML pairing and same variable names.
   - Confirm docs include local-vs-container note.

4. **Runtime immutability check**
   - Confirm no edits in:
     - `backend/src/models/factory.py`
     - `backend/src/agents/**`
     - `backend/src/config/app_config.py`

## ADR
- **Decision:** Implement cliproxyapi support via config/docs updates only, with optionality-safe examples.
- **Drivers:** Low regression risk, existing runtime support for `base_url` + `api_key`, clarity for users.
- **Alternatives considered:** Runtime fallback defaulting (`OPENAI_BASE_URL`), and strict mandatory base_url examples.
- **Why chosen:** Existing architecture already forwards required fields; the real gap is discoverability and environment-aware guidance.
- **Consequences:**
  - Positive: clear setup path without runtime churn.
  - Negative: documentation becomes slightly more complex due to local vs container endpoint guidance.
- **Follow-ups:** If recurring user confusion persists, propose a separate scoped enhancement for config validation hints (without changing model factory behavior).

## Plan Changelog
- v1: Initial consensus draft from deep-interview spec and codebase evidence.
- v2: Applied Architect/Critic feedback: added in-scope alternative, decision matrix, measurable ACs, explicit out-of-scope boundary, enforceable risk mitigations, concrete verification gates, and ADR consequence note.
