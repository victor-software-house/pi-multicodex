# @victor-software-house/pi-multicodex roadmap

## Product focus

`@victor-software-house/pi-multicodex` is a pi extension focused on rotating multiple ChatGPT Codex OAuth accounts for the `openai-codex-responses` API.

The roadmap is centered on:

- stable account management
- clear release and install paths
- maintainable internal structure
- better usage visibility for the active account
- a cleaner user experience inside pi

## Current product state

The current shipped behavior is:

- MultiCodex overrides the normal `openai-codex` provider path directly.
- MultiCodex auto-imports pi's stored `openai-codex` OAuth auth when it is new or changed.
- `/multicodex-use [identifier]` is the single account entrypoint.
  - with an identifier: use existing account or start login when missing/stale
  - with no argument: open account picker
- `/multicodex-status` shows managed account state.
- `/multicodex-footer` opens the footer settings panel.
- Footer settings are stored in `~/.pi/agent/settings.json` under `pi-multicodex`.
- Managed account storage is stored in `~/.pi/agent/codex-accounts.json`.

## Operating principles

- Keep npmjs as the canonical public distribution channel.
- Keep the package npm-installable for pi users.
- Use pnpm for local development.
- Keep releases small, validated, and repeatable.
- Prefer explicit behavior over hidden heuristics.
- Avoid custom encryption schemes for local secrets.
- If secret storage needs stronger protection later, prefer platform-backed secure storage over homegrown crypto.

## Decisions already locked in

- **Package name:** `@victor-software-house/pi-multicodex`
- **Commands:**
  - `/multicodex-use [identifier]`
  - `/multicodex-status`
  - `/multicodex-footer`
- **Scope:** Codex only
- **Local package manager:** pnpm
- **Primary release path:** npmjs with trusted publishing
- **Storage file:** `~/.pi/agent/codex-accounts.json`
- **Provider strategy:** own the normal `openai-codex` path directly
- **Auth strategy:** auto-import pi's stored `openai-codex` auth when it is new or changed
- **Footer config storage:** `settings.json` key `pi-multicodex`
- **Hook strategy:** `lefthook` runs `mise run pre-push` before push

## Current milestone — active-account usage footer polish

Goal: finish the Codex footer so it feels like the built-in usage experience rather than an add-on.

### Remaining work

- [x] Debounce model-change refresh work so rapid `Ctrl+P` cycling never blocks on auth sync or usage fetches
- [x] Render each reset countdown next to its matching usage period instead of grouping them at the end
- [x] Add live preview inside the `/multicodex-footer` panel
- [x] Update the actual footer while footer settings change in the panel
- [x] Tune the footer color palette before locking the final style
- [x] Tighten footer updates so account switches and quota rotation are reflected immediately
- [x] Add tests for live preview updates, model-switch debouncing, and footer/account synchronization

### Footer milestone status

The footer-polish work now covers:

1. **Model switching**
   - `model_select` renders cached state immediately.
   - Background refresh work is debounced so rapid `Ctrl+P` cycling does not block on auth sync or usage fetches.
   - Non-Codex model selection clears the footer immediately.

2. **Footer layout**
   - Each reset countdown now stays beside its matching usage period.
   - Current layout target is:
     - `Codex 5h:31% used (↺2h27m) 7d:87% used (↺2d6h) victor@...`

3. **Footer styling**
   - Labels stay dim.
   - Brand, account, and reset countdowns stay muted.
   - Percentages use severity coloring.

4. **Footer settings UX**
   - `/multicodex-footer` now shows a live preview.
   - The actual footer updates live while the panel is open.

5. **Footer/account synchronization**
   - Footer updates re-render immediately from cached state on account-manager state changes.
   - This keeps account and usage combinations aligned during account switches, usage refreshes, and quota rotation.

## Suggested implementation order for the next session

1. Start the behavior-contract documentation milestone.
2. Improve `/multicodex-use` picker and select-or-login flow.
3. Improve `/multicodex-status` output for active state, cooldowns, and manual override visibility.
4. Revisit footer colors only if real usage feedback shows readability issues.

## Follow-up milestone — behavior contract

Goal: make account rotation behavior explicit and documented.

- [ ] Define account selection priority
- [ ] Define quota exhaustion semantics
- [ ] Define which reset windows matter for selection
- [ ] Define retry policy
- [ ] Define manual override behavior
- [ ] Define when manual override clears
- [ ] Define cache TTL and refresh rules
- [ ] Define error classification rules
- [ ] Document the behavior contract in README or a dedicated doc

## Follow-up milestone — UX improvements

Goal: improve everyday usability for multi-account management.

- [ ] Improve the `/multicodex-use` account picker and select-or-login flow
- [ ] Improve the status output for account state, cooldowns, and manual selection
- [ ] Make active-account information easier to understand during a session

## Release discipline

Every release should continue to pass at least:

```bash
pnpm check
npm pack --dry-run
```

Target release flow:

1. Prepare the release locally with `npm run release:prepare -- <version>`.
2. Commit the prepared version bump.
3. Create and push a matching `v*` tag.
4. Let GitHub Actions publish through trusted publishing.

## Final release validation

Before the next real release, explicitly validate the full release path:

- [ ] Run `pnpm check`
- [ ] Run `npm pack --dry-run`
- [ ] Create and push the release tag
- [ ] Verify the GitHub Actions trusted-publishing workflow completes successfully
- [ ] Verify the new version is available on npmjs
- [ ] Verify install or upgrade in pi from the published package
- [ ] Verify the published tarball includes every runtime TypeScript module the extension imports

## Non-goals for now

- [ ] No cross-provider account orchestration
- [ ] No attempt to become a generic auth manager for pi
- [ ] No custom encryption implementation for local secrets
- [ ] No Bun-first consumer install story
