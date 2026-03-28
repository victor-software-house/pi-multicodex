import { promises as fs } from "node:fs";
import type { OAuthCredentials } from "@mariozechner/pi-ai/oauth";
import { getAgentAuthPath } from "pi-provider-utils/agent-paths";

const AUTH_FILE = getAgentAuthPath();
const IMPORTED_ACCOUNT_PREFIX = "OpenAI Codex";

interface AuthEntry {
	type?: string;
	access?: string | null;
	refresh?: string | null;
	expires?: number | null;
	accountId?: string | null;
	account_id?: string | null;
}

export interface ImportedOpenAICodexAuth {
	identifier: string;
	fingerprint: string;
	credentials: OAuthCredentials;
}

function asAuthEntry(value: unknown): AuthEntry | undefined {
	if (!value || typeof value !== "object" || Array.isArray(value)) {
		return undefined;
	}
	return value as AuthEntry;
}

function getAccountId(entry: AuthEntry): string | undefined {
	const accountId = entry.accountId ?? entry.account_id;
	return typeof accountId === "string" && accountId.trim()
		? accountId.trim()
		: undefined;
}

function getRequiredString(
	value: string | null | undefined,
): string | undefined {
	return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function createImportedIdentifier(accountId: string): string {
	return `${IMPORTED_ACCOUNT_PREFIX} ${accountId.slice(0, 8)}`;
}

function createFingerprint(entry: {
	access: string;
	refresh: string;
	expires: number;
	accountId?: string;
}): string {
	return JSON.stringify({
		access: entry.access,
		refresh: entry.refresh,
		expires: entry.expires,
		accountId: entry.accountId ?? null,
	});
}

export function parseImportedOpenAICodexAuth(
	auth: Record<string, unknown>,
): ImportedOpenAICodexAuth | undefined {
	const entry = asAuthEntry(auth["openai-codex"]);
	if (entry?.type !== "oauth") return undefined;

	const access = getRequiredString(entry.access);
	const refresh = getRequiredString(entry.refresh);
	const accountId = getAccountId(entry);
	const expires = entry.expires;
	if (!access || !refresh || typeof expires !== "number") {
		return undefined;
	}

	const credentials: OAuthCredentials = {
		access,
		refresh,
		expires,
		accountId,
	};
	return {
		identifier: createImportedIdentifier(accountId ?? "default"),
		fingerprint: createFingerprint({ access, refresh, expires, accountId }),
		credentials,
	};
}

/**
 * Write the active account's tokens to auth.json so pi's background features
 * (rename, compaction, inline suggestions) can resolve a valid API key through
 * the normal AuthStorage path.
 */
export async function writeActiveTokenToAuthJson(creds: {
	access: string;
	refresh: string;
	expires: number;
	accountId?: string;
}): Promise<void> {
	let auth: Record<string, unknown> = {};
	try {
		const raw = await fs.readFile(AUTH_FILE, "utf8");
		const parsed = JSON.parse(raw) as unknown;
		if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
			auth = parsed as Record<string, unknown>;
		}
	} catch {
		// File missing or corrupt — start fresh.
	}

	auth["openai-codex"] = {
		type: "oauth",
		access: creds.access,
		refresh: creds.refresh,
		expires: creds.expires,
		accountId: creds.accountId,
	};

	await fs.writeFile(AUTH_FILE, JSON.stringify(auth, null, 2));
}

export async function loadImportedOpenAICodexAuth(): Promise<
	ImportedOpenAICodexAuth | undefined
> {
	try {
		const raw = await fs.readFile(AUTH_FILE, "utf8");
		const parsed = JSON.parse(raw) as unknown;
		if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
			return undefined;
		}
		return parseImportedOpenAICodexAuth(parsed as Record<string, unknown>);
	} catch (error) {
		const withCode = error as Error & { code?: string };
		if (withCode.code === "ENOENT") {
			return undefined;
		}
		throw error;
	}
}
