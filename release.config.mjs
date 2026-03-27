export default {
	branches: ["main"],
	plugins: [
		[
			"@semantic-release/commit-analyzer",
			{
				preset: "conventionalcommits",
				releaseRules: [
					{ breaking: true, release: "major" },
					{ type: "feat", release: "minor" },
					{ type: "fix", release: "patch" },
					{ type: "perf", release: "patch" },
					{ type: "revert", release: "patch" },
				],
			},
		],
		"@semantic-release/release-notes-generator",
		[
			"@semantic-release/changelog",
			{
				changelogFile: "CHANGELOG.md",
			},
		],
		[
			"@semantic-release/npm",
			{
				npmPublish: true,
				pkgRoot: ".",
			},
		],
		[
			"@semantic-release/github",
			{
				successComment: false,
				failComment: false,
				releasedLabels: false,
			},
		],
		[
			"@semantic-release/git",
			{
				assets: ["package.json", "pnpm-lock.yaml", "CHANGELOG.md"],
				message: String.raw`chore(release): \${nextRelease.version} [skip ci]

\${nextRelease.notes}`,
			},
		],
	],
};
