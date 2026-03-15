import { describe, expect, it, vi } from "vitest";
import type { AccountManager } from "./account-manager";
import { registerCommands } from "./commands";
import type { createUsageStatusController } from "./status";

function createStatusControllerMock() {
	return {
		refreshFor: vi.fn().mockResolvedValue(undefined),
		openPreferencesPanel: vi.fn().mockResolvedValue(undefined),
		loadPreferences: vi.fn().mockResolvedValue(undefined),
		getPreferences: vi.fn(() => ({
			usageMode: "left",
			resetWindow: "7d",
			showAccount: true,
			showReset: true,
			order: "account-first",
		})),
	} as unknown as ReturnType<typeof createUsageStatusController>;
}

function createAccountManagerMock(emails: string[] = []) {
	return {
		getAccounts: () => emails.map((email) => ({ email })),
	} as unknown as AccountManager;
}

describe("registerCommands", () => {
	it("registers only the multicodex command", () => {
		const registerCommand = vi.fn();
		registerCommands(
			{ registerCommand } as never,
			createAccountManagerMock(),
			createStatusControllerMock(),
		);

		expect(registerCommand).toHaveBeenCalledTimes(1);
		expect(registerCommand).toHaveBeenCalledWith(
			"multicodex",
			expect.objectContaining({
				description: expect.any(String),
				handler: expect.any(Function),
				getArgumentCompletions: expect.any(Function),
			}),
		);
	});

	it("returns dynamic autocomplete for subcommands and managed account identifiers", () => {
		const registerCommand = vi.fn();
		registerCommands(
			{ registerCommand } as never,
			createAccountManagerMock(["alpha@example.com", "beta@example.com"]),
			createStatusControllerMock(),
		);

		const commandOptions = registerCommand.mock.calls[0]?.[1] as {
			getArgumentCompletions: (
				prefix: string,
			) => Array<{ value: string; label: string }> | null;
		};

		const subcommands = commandOptions.getArgumentCompletions("");
		expect(subcommands?.map((item) => item.value)).toContain("show");
		expect(subcommands?.map((item) => item.value)).toContain("use");

		const useAccounts = commandOptions.getArgumentCompletions("use a");
		expect(useAccounts).toEqual([
			{ value: "use alpha@example.com", label: "alpha@example.com" },
		]);
	});

	it("shows a non-interactive warning when no subcommand is provided", async () => {
		const registerCommand = vi.fn();
		registerCommands(
			{ registerCommand } as never,
			createAccountManagerMock(),
			createStatusControllerMock(),
		);

		const commandOptions = registerCommand.mock.calls[0]?.[1] as {
			handler: (args: string, ctx: unknown) => Promise<void>;
		};
		const notify = vi.fn();
		await commandOptions.handler("", {
			hasUI: false,
			ui: { notify },
		});

		expect(notify).toHaveBeenCalledWith(
			"/multicodex requires a subcommand in non-interactive mode. Use /multicodex help.",
			"warning",
		);
	});
});
