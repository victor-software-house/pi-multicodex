# @victor-software-house/pi-multicodex

![MultiCodex main panel](./assets/screenshots/multicodex-main.png)

MultiCodex is a [pi](https://github.com/badlogic/pi-mono) extension that manages multiple ChatGPT Codex accounts and rotates between them automatically when you hit quota limits.

You add your Codex accounts once. After that, MultiCodex transparently picks the best available account for every request. When one account runs dry mid-session, it switches to another and retries — no manual intervention needed.

## Getting started

Install from npm:

```bash
pi install npm:@victor-software-house/pi-multicodex
```

Restart pi. That is all you need — MultiCodex takes over the normal `openai-codex` provider path and auto-imports any Codex auth you have already set up in pi.

To manage your accounts inside a session, type `/multicodex`.

## How it works

When you start a session, MultiCodex:

1. Imports your existing pi Codex auth automatically (if present).
2. Checks usage data across all managed accounts.
3. Picks the best available account — untouched accounts first, then the one whose weekly reset window ends soonest, then a random available account as fallback.

If you pin a specific account with `/multicodex use`, that account is used until it hits quota or you clear the override.

When a request hits a quota or rate limit **before** any output is streamed, MultiCodex marks that account exhausted, picks the next available one, and retries. This happens up to 5 times transparently. If the manual override account fails, the override is cleared and rotation continues with the remaining accounts. Once output has started streaming, the error is surfaced as-is — no mid-stream account switching.

## Commands

Everything lives under one command: `/multicodex`.

| Command | What it does |
|---|---|
| `/multicodex` | Open the main interactive menu |
| `/multicodex show` | Print account status and cached usage |
| `/multicodex use [identifier]` | Activate an account, or open the picker if no identifier given |
| `/multicodex footer` | Configure the usage footer display |
| `/multicodex rotation` | Show the current rotation policy |
| `/multicodex verify` | Check that local storage paths are writable |
| `/multicodex path` | Print storage and settings file locations |
| `/multicodex reset [manual\|quota\|all]` | Clear manual override, quota cooldowns, or both |
| `/multicodex help` | Print a compact usage line |

All subcommands support dynamic autocomplete. `/multicodex use` also autocompletes from your managed account list.

Commands that do not need a UI panel (`show`, `verify`, `path`, `reset`, `help`) work in non-interactive mode too.

## Account picker

The `/multicodex use` picker lets you select, add, and remove accounts in one place.

![MultiCodex use picker](./assets/screenshots/multicodex-use-picker.png)

- **Enter** activates the highlighted account.
- **Backspace** removes it (after confirmation).

When you remove an active account, MultiCodex switches to the next available one automatically.

![MultiCodex remove account confirmation](./assets/screenshots/multicodex-remove-confirm.png)

## Usage footer

MultiCodex adds a live footer to your session showing the active account, 5-hour and 7-day usage percentages, and reset countdowns. The footer updates after every turn and on account switches.

You can customize which fields appear and their ordering with `/multicodex footer`.

![MultiCodex footer settings](./assets/screenshots/multicodex-footer-settings.png)

## What it does under the hood

- **Provider override.** MultiCodex registers itself as the `openai-codex` provider. You do not need to select a different provider or change your model — it works with whatever Codex model you already use.
- **Auth import.** When pi has stored Codex OAuth credentials, MultiCodex imports them automatically. You can also add accounts manually with `/multicodex use <email>`.
- **Token refresh.** OAuth tokens are refreshed before expiry so requests do not fail due to stale credentials.
- **Usage tracking.** Usage data is fetched from the Codex API and cached for 5 minutes per account. The footer renders cached data immediately and refreshes in the background.
- **Quota cooldown.** When an account is exhausted, it stays on cooldown until its next known reset time (or 1 hour if the reset time is unknown).

## Local development

This repo uses `mise` for tool versions and `pnpm` for dependency management.

```bash
mise install          # pin tool versions
pnpm install          # install dependencies
pnpm check            # lint + typecheck + test
npm pack --dry-run    # verify package contents
```

Run the extension directly during development:

```bash
pi -e ./index.ts
```

## Data storage

MultiCodex stores all data locally under `~/.pi/agent/`:

| File | Contents |
|---|---|
| `codex-accounts.json` | Managed account credentials and state |
| `settings.json` (key `pi-multicodex`) | Footer display preferences |

No data is sent anywhere except to the Codex API endpoints for auth refresh and usage queries.

## Release process

Releases are automated. Push a conventional commit to `main` and GitHub Actions handles versioning, changelog, npm publishing (via trusted publishing), and GitHub releases.

Local push protection via `lefthook` runs the same checks as CI before every push.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned work including configurable rotation settings, a shared controller architecture, and immediate footer persistence.

## Acknowledgment

This project descends from earlier MultiCodex work. Thanks to the original creator for the starting point that made this package possible.

The usage footer draws on ideas from [calesennett/pi-codex-usage](https://github.com/calesennett/pi-codex-usage). Thanks to its author for the reference implementation and footer design.
