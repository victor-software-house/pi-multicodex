import type { Account } from "./storage";
import {
	type CodexUsageSnapshot,
	getWeeklyResetAt,
	isUsageUntouched,
} from "./usage";

export function isAccountAvailable(account: Account, now: number): boolean {
	return !account.quotaExhaustedUntil || account.quotaExhaustedUntil <= now;
}

function pickRandomAccount(accounts: Account[]): Account | undefined {
	if (accounts.length === 0) return undefined;
	return accounts[Math.floor(Math.random() * accounts.length)];
}

function pickEarliestWeeklyResetAccount(
	accounts: Account[],
	usageByEmail: Map<string, CodexUsageSnapshot>,
): Account | undefined {
	const candidates = accounts
		.map((account) => ({
			account,
			resetAt: getWeeklyResetAt(usageByEmail.get(account.email)),
		}))
		.filter(
			(entry): entry is { account: Account; resetAt: number } =>
				typeof entry.resetAt === "number",
		)
		.sort((a, b) => a.resetAt - b.resetAt);

	return candidates[0]?.account;
}

export function pickBestAccount(
	accounts: Account[],
	usageByEmail: Map<string, CodexUsageSnapshot>,
	options?: { excludeEmails?: Set<string>; now?: number },
): Account | undefined {
	const now = options?.now ?? Date.now();
	const available = accounts.filter(
		(account) =>
			isAccountAvailable(account, now) &&
			!options?.excludeEmails?.has(account.email),
	);
	if (available.length === 0) return undefined;

	const withUsage = available.filter((account) =>
		usageByEmail.has(account.email),
	);
	const untouched = withUsage.filter((account) =>
		isUsageUntouched(usageByEmail.get(account.email)),
	);

	if (untouched.length > 0) {
		return (
			pickEarliestWeeklyResetAccount(untouched, usageByEmail) ??
			pickRandomAccount(untouched)
		);
	}

	const earliestWeeklyReset = pickEarliestWeeklyResetAccount(
		withUsage,
		usageByEmail,
	);
	if (earliestWeeklyReset) return earliestWeeklyReset;

	return pickRandomAccount(available);
}
