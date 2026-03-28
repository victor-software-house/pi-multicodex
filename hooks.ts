import type { AccountManager } from "./account-manager";

type WarningHandler = (message: string) => void;

async function refreshAndActivateBestAccount(
	accountManager: AccountManager,
	warningHandler?: WarningHandler,
): Promise<void> {
	await accountManager.syncImportedOpenAICodexAuth();
	await accountManager.refreshUsageForAllAccounts({ force: true });

	const needsReauth = accountManager.getAccountsNeedingReauth();
	if (needsReauth.length > 0) {
		const hints = needsReauth.map((a) => {
			const cmd = a.importSource
				? "/login openai-codex"
				: `/multicodex use ${a.email}`;
			return `${a.email} (${cmd})`;
		});
		warningHandler?.(
			`Multicodex: ${needsReauth.length} account(s) need re-authentication: ${hints.join(", ")}`,
		);
	}

	const manual = accountManager.getAvailableManualAccount();
	if (manual) return;
	if (accountManager.hasManualAccount()) {
		accountManager.clearManualAccount();
	}
	await accountManager.activateBestAccount();
}

export function handleSessionStart(
	accountManager: AccountManager,
	warningHandler?: WarningHandler,
): void {
	if (accountManager.getAccounts().length === 0) return;
	void refreshAndActivateBestAccount(accountManager, warningHandler);
}

export function handleNewSessionSwitch(
	accountManager: AccountManager,
	warningHandler?: WarningHandler,
): void {
	void refreshAndActivateBestAccount(accountManager, warningHandler);
}
