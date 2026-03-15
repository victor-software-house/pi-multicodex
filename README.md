# @victor-software-house/pi-multicodex

![MultiCodex](./assets/multicodex.png)

`@victor-software-house/pi-multicodex` is a pi extension that rotates multiple ChatGPT Codex OAuth accounts for the `openai-codex-responses` API.

## What it does

- overrides the normal `openai-codex` path instead of requiring a separate provider to be selected
- auto-imports pi's stored `openai-codex` auth when it is new or changed
- rotates accounts on quota and rate-limit failures
- prefers untouched accounts when usage data is available
- otherwise prefers the account whose weekly window resets first
- keeps the implementation focused on Codex account rotation

## Install

```bash
pi install npm:@victor-software-house/pi-multicodex
```

Restart `pi` after installation.

## Local development

This repo uses `mise` to pin tools and `pnpm` for dependency management.

```bash
mise install
pnpm install
pnpm check
```

Equivalent mise tasks:

```bash
mise run install
mise run check
mise run pack-dry
```

Run the extension directly during local development:

```bash
pi -e ./index.ts
```

## Commands

- `/multicodex-use [identifier]`
  - Use an existing managed account, or start the Codex login flow when the account is missing or the stored auth is no longer valid.
  - With no argument, opens an account picker.
- `/multicodex-status`
  - Show managed account state and cached usage information.
- `/multicodex-footer`
  - Open an interactive panel to configure footer fields and ordering.

## Project direction

This project is maintained as its own package and release line.

Current direction:

- package name: `@victor-software-house/pi-multicodex`
- Codex-only scope
- local state stored at `~/.pi/agent/codex-accounts.json`
- internal logic split into focused modules
- current roadmap tracked in `ROADMAP.md`

Current next step:

- refine the footer color palette with small visual adjustments only
- document the account-rotation behavior contract explicitly
- improve the `/multicodex-use` and `/multicodex-status` everyday UX

## Behavior contract

The current runtime behavior is:

### Account selection priority

1. Use the manual account selected with `/multicodex-use` when it is still available.
2. Otherwise clear the stale manual override and select the best available managed account.
3. Best-account selection prefers:
   - untouched accounts with usage data
   - then the account whose weekly reset window ends first
   - then a random available account as fallback

### Quota exhaustion semantics

- Quota and rate-limit style failures are detected from provider error text.
- When a request fails before any output is streamed, MultiCodex marks that account exhausted and retries on another account.
- Exhaustion lasts until the next known reset time.
- If usage data does not provide a reset time, exhaustion falls back to a 1 hour cooldown.

### Retry policy

- MultiCodex retries account rotation up to 5 times for a single request.
- Retries only happen for quota/rate-limit style failures that occur before output is forwarded.
- Once output has started streaming, the original error is surfaced instead of rotating.

### Manual override behavior

- `/multicodex-use <identifier>` sets the manual account override immediately.
- `/multicodex-use` with no argument opens the account picker and sets the selected manual override.
- Manual override is session-local state.
- Manual override clears automatically when the selected account is no longer available or when it hits quota during rotation.

### Usage cache and refresh rules

- Usage is cached in memory for 5 minutes per account.
- Footer updates render cached usage immediately and refresh in the background when needed.
- Rapid `model_select` changes debounce background refresh work so non-Codex model switching clears the footer immediately.

### Error classification

Quota rotation currently treats these error classes as interchangeable:

- HTTP `429`
- `quota`
- `usage limit`
- `rate limit`
- `too many requests`
- `limit reached`

## Release validation

Minimum release checks:

```bash
pnpm check
npm pack --dry-run
```

Release flow:

1. Prepare the release locally.
2. Commit the version bump.
3. Create and push a matching `v*` tag.
4. Let GitHub Actions publish through trusted publishing.

Local push protection:

- `lefthook` runs `mise run pre-push`
- the `pre-push` mise task runs the same core validations as the publish workflow:
  - `pnpm check`
  - `npm pack --dry-run`

Prepare locally:

```bash
npm run release:prepare -- <version>
```

The helper updates `package.json` with `bun pm pkg set` and then runs the release checks.

Example:

```bash
git add package.json
git commit -m "release: v<version>"
git tag v<version>
git push origin main --tags
```

Do not use local `npm publish` for normal releases in this repo.

## Acknowledgment

This project descends from earlier MultiCodex work. Thanks to the original creator for the starting point that made this package possible.

The active-account usage footer work also draws on ideas from `calesennett/pi-codex-usage`. Thanks to its author for the reference implementation and footer design.
