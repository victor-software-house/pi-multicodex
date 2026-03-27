import { getApiProvider } from "@mariozechner/pi-ai";
import { mirrorProvider } from "pi-provider-utils/providers";
import type { AccountManager } from "./account-manager";
import { createStreamWrapper } from "./stream-wrapper";

export const PROVIDER_ID = "openai-codex";

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
	const mirror = mirrorProvider("openai-codex");
	if (!mirror) {
		return { baseUrl: "https://chatgpt.com/backend-api", models: [] };
	}
	return {
		baseUrl: mirror.baseUrl,
		models: mirror.models.map((m) => ({
			id: m.id,
			name: m.name,
			reasoning: m.reasoning,
			input: [...m.input],
			cost: { ...m.cost },
			contextWindow: m.contextWindow,
			maxTokens: m.maxTokens,
		})),
	};
}

export function buildMulticodexProviderConfig(accountManager: AccountManager) {
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
		api: "openai-codex-responses" as const,
		streamSimple: createStreamWrapper(accountManager, baseProvider),
		models: mirror.models,
	};
}
