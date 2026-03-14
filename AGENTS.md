# MultiCodex Extension - Agent Notes

## Scope

Only edit files in this directory:

```
~/.pi/agent/extensions/multicodex/
```

## Goals

- Keep the extension runnable when installed outside the pi monorepo.
- Avoid deep imports that resolve to repo-local paths.
- Keep runtime behavior compatible with pi extension docs.

## Type Safety

- Use public exports from `@mariozechner/pi-ai` and `@mariozechner/pi-coding-agent`.
- The local `pi-coding-agent.d.ts` module augmentation is for TypeScript only and must stay minimal.

## Checks

Run:

```bash
npm run lint
npm run tsgo
npm run test
```

Release validation:

```bash
npm pack --dry-run
```

## Commit Workflow

- Do not batch unrelated changes into a single large commit.
- Commit incrementally as each logical step is completed.
- Use conventional commit messages such as `build: ...`, `docs: ...`, `refactor: ...`, and `release: ...`.
- Before publishing, make sure the working tree is clean and all required checks pass.
- Keep release commits focused on version bumps and release metadata only.
