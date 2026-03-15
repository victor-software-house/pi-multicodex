#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pillow"]
# ///

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("assets/screenshots")

# Palette aligned to your control-sequence samples + current iTerm2 profile.
# iTerm2 Default profile background: #141414 (20, 20, 20)
BG = (20, 20, 20)
# iTerm2 Default profile foreground: #FFFFD4 (255, 255, 212)
DEFAULT = (255, 255, 212)
ACCENT = (225, 196, 125)  # 38:2:1:225:196:125
DIM = (75, 75, 75)  # 38:2:1:75:75:75
SUCCESS = (166, 211, 147)  # 38:2:1:166:211:147


@dataclass(frozen=True)
class Screen:
	filename: str
	title: str
	lines: list[str]
	footer_path: str
	footer_status: str
	account_label: str
	five_hour_usage: str
	seven_day_usage: str


def load_font(size: int) -> ImageFont.FreeTypeFont:
	for candidate in (
		"/System/Library/Fonts/Menlo.ttc",
		"/System/Library/Fonts/SFNSMono.ttf",
	):
		path = Path(candidate)
		if path.exists():
			return ImageFont.truetype(str(path), size=size)
	return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
	left, _top, right, _bottom = draw.textbbox((0, 0), text, font=font)
	return right - left


def draw_colored_footer(
	draw: ImageDraw.ImageDraw,
	x: int,
	y: int,
	font: ImageFont.ImageFont,
	screen: Screen,
) -> None:
	x_cursor = x
	segments = [
		("Codex", DIM),
		(" · ", DIM),
		(screen.five_hour_usage, SUCCESS),
		(" · ", DIM),
		(screen.seven_day_usage, SUCCESS),
		(" · ", DIM),
		(screen.account_label, DEFAULT),
	]
	for segment, color in segments:
		draw.text((x_cursor, y), segment, fill=color, font=font)
		x_cursor += text_width(draw, segment, font)


def draw_screen(screen: Screen, font: ImageFont.ImageFont) -> None:
	padding_x = 28
	padding_y = 24
	line_height = 44
	footer_line_height = 38

	sample_lines = [
		screen.title,
		*screen.lines,
		screen.footer_path,
		screen.footer_status,
		screen.account_label,
		screen.five_hour_usage,
		screen.seven_day_usage,
	]
	max_chars = max(len(line) for line in sample_lines)
	char_width = 22
	content_width = max_chars * char_width
	width = max(1600, content_width + padding_x * 2)
	height = (
		padding_y
		+ 40
		+ 26
		+ line_height
		+ len(screen.lines) * line_height
		+ 30
		+ footer_line_height * 3
		+ padding_y
	)

	image = Image.new("RGB", (width, height), BG)
	draw = ImageDraw.Draw(image)

	top_border_y = padding_y
	draw.line((padding_x, top_border_y, width - padding_x, top_border_y), fill=ACCENT, width=2)

	title_y = top_border_y + 28
	draw.text((padding_x + 6, title_y), screen.title, fill=ACCENT, font=font)

	start_y = title_y + 60
	for index, line in enumerate(screen.lines):
		if line.startswith("→"):
			color = ACCENT
		elif line.startswith("↑↓"):
			color = DIM
		else:
			color = DEFAULT
		draw.text((padding_x + 6, start_y + index * line_height), line, fill=color, font=font)

	bottom_border_y = start_y + len(screen.lines) * line_height + 16
	draw.line((padding_x, bottom_border_y, width - padding_x, bottom_border_y), fill=ACCENT, width=2)

	footer_y = bottom_border_y + 24
	draw.text((padding_x + 6, footer_y), screen.footer_path, fill=DIM, font=font)
	draw.text((padding_x + 6, footer_y + footer_line_height), screen.footer_status, fill=DIM, font=font)
	draw_colored_footer(draw, padding_x + 6, footer_y + footer_line_height * 2, font, screen)

	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	image.save(OUTPUT_DIR / screen.filename)


SCREENS = [
	Screen(
		filename="multicodex-main.png",
		title="MultiCodex",
		lines=[
			"→ use: select, activate, or remove managed account",
			"  show: managed account and usage summary",
			"  footer: footer settings panel",
			"  rotation: current rotation behavior",
			"  verify: runtime health checks",
			"  path: storage and settings locations",
			"  reset: clear manual or quota state",
			"  help: command usage",
			"",
			"↑↓ navigate   enter select   escape/ctrl+c cancel",
		],
		footer_path="~/workspace/<org>/pi-multicodex (main)",
		footer_status="↑479k ↓38k R9.5M $3.039 (sub) 36.8%/272k (auto)            (openai-codex) gpt-5.3-codex • high",
		account_label="account-01@example.test",
		five_hour_usage="5h:73% left (↺1h7m)",
		seven_day_usage="7d:92% left (↺6d20h)",
	),
	Screen(
		filename="multicodex-use-picker.png",
		title="Select Account",
		lines=[
			"Enter: use  Backspace: remove account  Esc: cancel",
			"",
			"→ account-01@example.test",
			"  account-02@example.test (Quota)",
			"  account-03@example.test",
			"  imported-account@example.test",
			"",
			"↑↓ navigate   enter select   backspace remove",
		],
		footer_path="~/workspace/<org>/pi-multicodex (main)",
		footer_status="↑462k ↓31k R8.7M $2.901 (sub) 35.2%/272k (auto)            (openai-codex) gpt-5.3-codex • high",
		account_label="account-01@example.test",
		five_hour_usage="5h:64% left (↺2h14m)",
		seven_day_usage="7d:89% left (↺6d19h)",
	),
	Screen(
		filename="multicodex-remove-confirm.png",
		title="Remove account",
		lines=[
			"Remove account-01@example.test?",
			"This account is currently active and MultiCodex will switch to another account.",
			"",
			"→ Yes, remove",
			"  No, keep account",
			"",
			"↑↓ navigate   enter confirm   esc cancel",
		],
		footer_path="~/workspace/<org>/pi-multicodex (main)",
		footer_status="↑462k ↓31k R8.7M $2.901 (sub) 35.2%/272k (auto)            (openai-codex) gpt-5.3-codex • high",
		account_label="account-01@example.test",
		five_hour_usage="5h:64% left (↺2h14m)",
		seven_day_usage="7d:89% left (↺6d19h)",
	),
]


if __name__ == "__main__":
	font = load_font(36)
	for screen in SCREENS:
		draw_screen(screen, font)
	print(f"Wrote {len(SCREENS)} synthetic screenshots to {OUTPUT_DIR}")
