# Sticky Session Operations Context

## Purpose and Scope

This capability covers operational control of sticky-session mappings after prompt-cache affinity was made bounded. It distinguishes durable backend/session routing from bounded prompt-cache affinity and defines the admin controls around those mappings.

See `openspec/specs/sticky-session-operations/spec.md` for normative requirements.

## Decisions

- Sticky-session rows store an explicit `kind` so prompt-cache cleanup can target only bounded mappings.
- Dashboard prompt-cache TTL is persisted in settings so operators can adjust it without restart.
- Background cleanup removes stale prompt-cache rows proactively, while manual delete and purge endpoints provide operator override.
- Dashboard sticky threads are treated as an operator-selected routing policy, not as a migration-time forced rollout for existing installations. Fresh installs may seed the setting enabled by default, but upgrades should not silently flip an existing deployment's routing behavior.

## Constraints

- Historical sticky-session rows created before the `kind` column are backfilled conservatively to a durable kind to avoid accidental purge.
- Durable `codex_session` and `sticky_thread` mappings are never deleted by automatic cleanup.
- Sticky threads and prompt-cache affinity solve different problems. Sticky threads keep conversation turns on the same upstream account when the route depends on dashboard thread affinity, while prompt-cache affinity keeps repeated cache-keyed `/v1` requests warm only within a bounded TTL.
- Disabling sticky threads can increase token usage on long-running conversations for routes that rely on dashboard thread affinity, because later turns may land on a different upstream account and need to replay more prior context instead of reusing the same account-local conversation path.

## Failure Modes

- Cleanup failures are logged and retried on the next interval; request handling continues.
- Manual purge and delete operations are dashboard-auth protected and return normal dashboard API errors on invalid input or missing keys.

## Example

- A dashboard operator keeps sticky threads enabled for a long-lived conversational workflow so follow-up turns stay on the same upstream account.
- If the operator disables sticky threads for that workflow, later turns can be routed to a different account. When that happens, the client may need to resend a larger slice of conversation history to recover context, which increases token consumption in long-context sessions.

## Operational Notes

- Prefer leaving sticky threads enabled for long-running chat-style sessions unless you have a specific balancing reason to disable them.
- If operators turn sticky threads off, monitor for increased prompt sizes, higher token spend, and user reports that long conversations lose continuity when requests rebalance across accounts.
- See `openspec/specs/sticky-session-operations/spec.md` for the normative sticky-session and cleanup requirements, and `openspec/specs/responses-api-compat/spec.md` for Codex/session-specific routing contracts that can preserve continuity independently of the dashboard toggle.
