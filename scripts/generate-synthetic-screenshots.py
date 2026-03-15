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

PADDING_X = 28
PADDING_Y = 24
LINE_HEIGHT = 44
FOOTER_LINE_HEIGHT = 38
FONT_SIZE = 36


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


def create_canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
	image = Image.new("RGB", (width, height), BG)
	return image, ImageDraw.Draw(image)


def draw_segmented_text(
	draw: ImageDraw.ImageDraw,
	x: int,
	y: int,
	font: ImageFont.ImageFont,
	segments: list[tuple[str, tuple[int, int, int]]],
) -> None:
	x_cursor = x
	for text, color in segments:
		draw.text((x_cursor, y), text, fill=color, font=font)
		x_cursor += text_width(draw, text, font)


def draw_colored_footer(
	draw: ImageDraw.ImageDraw,
	x: int,
	y: int,
	font: ImageFont.ImageFont,
	account_label: str,
	five_hour_usage: str,
	seven_day_usage: str,
) -> None:
	draw_segmented_text(
		draw,
		x,
		y,
		font,
		[
			("Codex", DIM),
			(" · ", DIM),
			(five_hour_usage, SUCCESS),
			(" · ", DIM),
			(seven_day_usage, SUCCESS),
			(" · ", DIM),
			(account_label, DEFAULT),
		],
	)


def save_image(image: Image.Image, filename: str) -> None:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	image.save(OUTPUT_DIR / filename)


def draw_standard_screen(screen: Screen, font: ImageFont.ImageFont) -> None:
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
	width = max(1600, content_width + PADDING_X * 2)
	height = (
		PADDING_Y
		+ 40
		+ 26
		+ LINE_HEIGHT
		+ len(screen.lines) * LINE_HEIGHT
		+ 30
		+ FOOTER_LINE_HEIGHT * 3
		+ PADDING_Y
	)

	image, draw = create_canvas(width, height)

	top_border_y = PADDING_Y
	draw.line(
		(PADDING_X, top_border_y, width - PADDING_X, top_border_y),
		fill=ACCENT,
		width=2,
	)

	title_y = top_border_y + 28
	draw.text((PADDING_X + 6, title_y), screen.title, fill=ACCENT, font=font)

	start_y = title_y + 60
	for index, line in enumerate(screen.lines):
		if line.startswith("→"):
			color = ACCENT
		elif line.startswith("↑↓"):
			color = DIM
		else:
			color = DEFAULT
		draw.text((PADDING_X + 6, start_y + index * LINE_HEIGHT), line, fill=color, font=font)

	bottom_border_y = start_y + len(screen.lines) * LINE_HEIGHT + 16
	draw.line(
		(PADDING_X, bottom_border_y, width - PADDING_X, bottom_border_y),
		fill=ACCENT,
		width=2,
	)

	footer_y = bottom_border_y + 24
	draw.text((PADDING_X + 6, footer_y), screen.footer_path, fill=DIM, font=font)
	draw.text(
		(PADDING_X + 6, footer_y + FOOTER_LINE_HEIGHT),
		screen.footer_status,
		fill=DIM,
		font=font,
	)
	draw_colored_footer(
		draw,
		PADDING_X + 6,
		footer_y + FOOTER_LINE_HEIGHT * 2,
		font,
		screen.account_label,
		screen.five_hour_usage,
		screen.seven_day_usage,
	)

	save_image(image, screen.filename)


def draw_footer_settings_screen(font: ImageFont.ImageFont) -> None:
	filename = "multicodex-footer-settings.png"
	title = "MultiCodex Footer"
	subtitle = "Configure the usage footer to match the codex usage extension style."
	footer_path = "~/workspace/<org>/pi-multicodex (main)"
	footer_status = "↑612k ↓67k R26M W346k $12.199 (sub) 67.0%/272k (auto)            (openai-codex) gpt-5.4 • high"
	account_label = "account-01@example.test"
	five_hour_usage = "5h:68% left (↺14m)"
	seven_day_usage = "7d:90% left (↺6d19h)"

	lines_for_width = [
		title,
		subtitle,
		"Preview: Codex · 5h:68% left (↺14m) · 7d:90% left (↺6d19h) · account-01@example.test",
		"→ Usage display         left",
		"  Reset countdown window  both",
		"  Show account            on",
		"  Show reset countdown    on",
		"  Footer order            usage-first",
		"  Show remaining or consumed quota percentages",
		"  Type to search · Enter/Space to change · Esc to cancel",
		footer_path,
		footer_status,
		account_label,
		five_hour_usage,
		seven_day_usage,
	]
	char_width = 22
	width = max(1800, max(len(line) for line in lines_for_width) * char_width + PADDING_X * 2)
	height = 920

	image, draw = create_canvas(width, height)

	top_border_y = PADDING_Y
	draw.line(
		(PADDING_X, top_border_y, width - PADDING_X, top_border_y),
		fill=ACCENT,
		width=2,
	)

	y = top_border_y + 28
	draw.text((PADDING_X + 6, y), title, fill=ACCENT, font=font)
	y += 60
	draw.text((PADDING_X + 6, y), subtitle, fill=DIM, font=font)
	y += 52
	draw_segmented_text(
		draw,
		PADDING_X + 6,
		y,
		font,
		[
			("Preview", DIM),
			(": ", DEFAULT),
			("Codex", DIM),
			(" · ", DIM),
			(five_hour_usage, SUCCESS),
			(" · ", DIM),
			(seven_day_usage, SUCCESS),
			(" · ", DIM),
			(account_label, DEFAULT),
		],
	)
	y += 64

	settings_data = [
		("→ ", "Usage display", "left", True),
		("  ", "Reset countdown window", "both", False),
		("  ", "Show account", "on", False),
		("  ", "Show reset countdown", "on", False),
		("  ", "Footer order", "usage-first", False),
	]
	label_max = max(len(label) for _, label, _, _ in settings_data)
	value_col = PADDING_X + 6 + text_width(draw, "→ " + "x" * label_max + "  ", font)
	for prefix, label, value, selected in settings_data:
		label_color = ACCENT if selected else DEFAULT
		value_color = ACCENT if selected else DIM
		prefix_color = ACCENT if selected else DEFAULT
		draw.text((PADDING_X + 6, y), prefix, fill=prefix_color, font=font)
		px = PADDING_X + 6 + text_width(draw, prefix, font)
		draw.text((px, y), label, fill=label_color, font=font)
		draw.text((value_col, y), value, fill=value_color, font=font)
		y += LINE_HEIGHT

	y += 18
	draw.text(
		(PADDING_X + 44, y),
		"Show remaining or consumed quota percentages",
		fill=DIM,
		font=font,
	)
	y += 68
	draw.text(
		(PADDING_X + 44, y),
		"Type to search · Enter/Space to change · Esc to cancel",
		fill=DIM,
		font=font,
	)

	bottom_border_y = height - (FOOTER_LINE_HEIGHT * 3 + 46)
	draw.line(
		(PADDING_X, bottom_border_y, width - PADDING_X, bottom_border_y),
		fill=ACCENT,
		width=2,
	)

	footer_y = bottom_border_y + 24
	draw.text((PADDING_X + 6, footer_y), footer_path, fill=DIM, font=font)
	draw.text((PADDING_X + 6, footer_y + FOOTER_LINE_HEIGHT), footer_status, fill=DIM, font=font)
	draw_colored_footer(
		draw,
		PADDING_X + 6,
		footer_y + FOOTER_LINE_HEIGHT * 2,
		font,
		account_label,
		five_hour_usage,
		seven_day_usage,
	)

	save_image(image, filename)


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
	font = load_font(FONT_SIZE)
	for screen in SCREENS:
		draw_standard_screen(screen, font)
	draw_footer_settings_screen(font)
	print(f"Wrote {len(SCREENS) + 1} synthetic screenshots to {OUTPUT_DIR}")
