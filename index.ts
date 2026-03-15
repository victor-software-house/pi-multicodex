/*
 * MultiCodex Extension
 *
 * Rotates multiple ChatGPT Codex OAuth accounts for the built-in
 * openai-codex-responses API.
 */

import {
	type Api,
	type AssistantMessageEventStream,
	type Context,
	getApiProvider,
	getModels,
	type Model,
	type SimpleStreamOptions,
} from "@mariozechner/pi-ai";
import type {
	ExtensionAPI,
	ExtensionContext,
} from "@mariozechner/pi-coding-agent";
import { AccountManager } from "./account-manager";
import { registerCommands } from "./commands";
import { handleNewSessionSwitch, handleSessionStart } from "./hooks";
import { createStreamWrapper } from "./stream-wrapper";

// =============================================================================
// Helpers
// =============================================================================

export { AccountManager } from "./account-manager";
export {
	isAccountAvailable,
	pickBestAccount,
} from "./selection";
export type { Account } from "./storage";
export { createStreamWrapper } from "./stream-wrapper";
export type { CodexUsageSnapshot } from "./usage";
export {
	formatResetAt,
	getNextResetAt,
	getWeeklyResetAt,
	isUsageUntouched,
	parseCodexUsageResponse,
} from "./usage";

export function isQuotaErrorMessage(message: string): boolean {
	return /\b429\b|quota|usage limit|rate.?limit|too many requests|limit reached/i.test(
		message,
	);
}

export interface ProviderModelDef {
	id: string;
	name: string;
	reasoning: boolean;
	input: ("text" | "image")[];
	cost: {
		input: number;
		output: number;
		cacheRead: number;
		cacheWrite: number;
	};
	contextWindow: number;
	maxTokens: number;
}

export function getOpenAICodexMirror(): {
	baseUrl: string;
	models: ProviderModelDef[];
} {
	const sourceModels = getModels("openai-codex");
	return {
		baseUrl: sourceModels[0]?.baseUrl || "https://chatgpt.com/backend-api",
		models: sourceModels.map((m) => ({
			id: m.id,
			name: m.name,
			reasoning: m.reasoning,
			input: m.input,
			cost: m.cost,
			contextWindow: m.contextWindow,
			maxTokens: m.maxTokens,
		})),
	};
}

// =============================================================================
// Storage
// =============================================================================

const PROVIDER_ID = "multicodex";

// =============================================================================
// Extension Entry Point
// =============================================================================

export function buildMulticodexProviderConfig(accountManager: AccountManager): {
	baseUrl: string;
	apiKey: string;
	api: "openai-codex-responses";
	streamSimple: (
		model: Model<Api>,
		context: Context,
		options?: SimpleStreamOptions,
	) => AssistantMessageEventStream;
	models: ProviderModelDef[];
} {
	const mirror = getOpenAICodexMirror();
	const baseProvider = getApiProvider("openai-codex-responses");
	if (!baseProvider) {
		throw new Error(
			"OpenAI Codex provider not available. Please update pi to include openai-codex support.",
		);
	}
	return {
		baseUrl: mirror.baseUrl,
		apiKey: "managed-by-extension",
		api: "openai-codex-responses",
		streamSimple: createStreamWrapper(accountManager, baseProvider),
		models: mirror.models,
	};
}

export default function multicodexExtension(pi: ExtensionAPI) {
	const accountManager = new AccountManager();
	let lastContext: ExtensionContext | undefined;

	accountManager.setWarningHandler((message) => {
		if (lastContext) {
			lastContext.ui.notify(message, "warning");
		}
	});

	pi.registerProvider(
		PROVIDER_ID,
		buildMulticodexProviderConfig(accountManager),
	);

	registerCommands(pi, accountManager);

	// Hooks
	pi.on("session_start", (_event: unknown, ctx: ExtensionContext) => {
		lastContext = ctx;
		handleSessionStart(accountManager);
	});

	pi.on(
		"session_switch",
		(event: { reason?: string }, ctx: ExtensionContext) => {
			lastContext = ctx;
			if (event.reason === "new") {
				handleNewSessionSwitch(accountManager);
			}
		},
	);
}
