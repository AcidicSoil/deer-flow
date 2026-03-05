# Deep Interview Spec: cliproxyapi-capable OpenAI configuration

## Metadata
- Interview ID: di-cliproxyapi-openai-config-20260305
- Rounds: 2
- Final Ambiguity Score: 17.25%
- Type: brownfield
- Generated: 2026-03-05
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.95 | 0.35 | 0.3325 |
| Constraint Clarity | 0.90 | 0.25 | 0.2250 |
| Success Criteria | 0.85 | 0.25 | 0.2125 |
| Context Clarity | 0.85 | 0.15 | 0.1275 |
| **Total Clarity** | | | **0.8975** |
| **Ambiguity** | | | **0.1725 (17.25%)** |

## Goal
Enable OpenAI model configuration to work cleanly with a local OpenAI-compatible cliproxyapi endpoint by adding explicit config and documentation support for `OPENAI_BASE_URL` and API key routing, without changing runtime model/factory behavior.

## Constraints
- Brownfield change only; reuse existing config-loading and model-factory behavior.
- Keep runtime behavior unchanged (no factory/agent execution-path modifications).
- Add clear, explicit setup paths for local proxy endpoint `http://127.0.0.1:8317/v1`.
- Keep OpenAI-compatible configuration idioms already used in project (`langchain_openai:ChatOpenAI`, env interpolation with `$VARS`).

## Non-Goals
- No new provider abstraction or API gateway logic in runtime code.
- No changes to request/response transformation logic.
- No automatic fallback precedence logic between multiple key/base-url vars.

## Acceptance Criteria
- [ ] `.env.example` includes `OPENAI_BASE_URL` and API key guidance for cliproxyapi usage.
- [ ] `config.example.yaml` includes an OpenAI model example showing `base_url: $OPENAI_BASE_URL` and API key variable usage.
- [ ] User-facing docs (README and/or backend configuration docs) include explicit local proxy example using `http://127.0.0.1:8317/v1` and explain key routing expectations.
- [ ] No runtime code changes are introduced in model factory/agent execution paths.

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| Runtime code likely needs changes for proxy support | Checked existing factory/config flow in brownfield code | Existing flow already passes `base_url` + `api_key`; focus on config/docs only |
| User might want fallback logic changes | Asked scope selection directly | User selected config/docs-only path |
| Criteria might be partial | Asked MUST-have acceptance criteria checklist | User confirmed all applicable listed criteria are required |

## Technical Context
Relevant brownfield findings:
- `config.example.yaml` already demonstrates OpenAI-compatible model config and supports `base_url` in examples.
- `backend/src/config/app_config.py` resolves `$ENV_VAR` values for config fields.
- `backend/src/models/factory.py` preserves and forwards extra model config fields (including `api_key` / `base_url`) to provider constructors.
- `.env.example` currently documents `OPENAI_API_KEY` but not `OPENAI_BASE_URL`.
- README/config docs currently emphasize API key setup but do not clearly document local cliproxyapi endpoint usage.

## Ontology (Key Entities)
| Entity | Fields | Relationships |
|--------|--------|---------------|
| Environment Config | `OPENAI_API_KEY`, `OPENAI_BASE_URL` | Injected into YAML config via `$VARS` expansion |
| Model Config Entry | `use`, `model`, `api_key`, `base_url` | Consumed by model factory to instantiate `ChatOpenAI` |
| OpenAI-Compatible Proxy | Endpoint URL (`http://127.0.0.1:8317/v1`), proxy API key | Target for `ChatOpenAI` requests when `base_url` is set |
| Documentation | setup steps, examples, notes | Guides users to valid env+config for local proxy use |

## Interview Transcript
<details>
<summary>Full Q&A (2 rounds)</summary>

### Round 1
**Q:** Which behavior do you want implemented for OpenAI configs?
**A:** Config/docs only.
**Ambiguity:** 34.75% (Goal: 0.90, Constraints: 0.85, Criteria: 0.45, Context: 0.85)

### Round 2
**Q:** Which acceptance criteria are MUST-HAVE?
**A:** All listed applicable criteria are must-have.
**Ambiguity:** 17.25% (Goal: 0.95, Constraints: 0.90, Criteria: 0.85, Context: 0.85)

</details>
