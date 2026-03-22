"""光标与输入文字的轻量可视快照脚本。

用途：
- 生成 50% / 100% / 200% 缩放下的截图，便于肉眼比对光标与文字的对齐效果。
- 产出完整画面截图 + 输入框局部截图 + 三倍率拼接对比图。

运行：
    python test/visual/cursor_visual_snapshot.py

输出目录：
    test/visual/output/cursor_snapshots/
"""

from __future__ import annotations

import importlib
import os
import random
from pathlib import Path

# 让脚本在无窗口环境下也能产图
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "test" / "visual" / "output" / "cursor_snapshots"
SCALES = [0.5, 1.0, 2.0]


def _reload_modules_for_scale(scale: float):
    os.environ["TYPING_GAME_SCALE_RATIO"] = str(scale)

    import conf.game_constants as gc_mod
    import typing_game as tg_mod

    gc_mod = importlib.reload(gc_mod)
    tg_mod = importlib.reload(tg_mod)
    return gc_mod, tg_mod


def _render_single_scale(scale: float):
    gc_mod, tg_mod = _reload_modules_for_scale(scale)

    random.seed(42)
    game = tg_mod.TypingGame()
    game.state = game.STATE_PLAYING
    game.mode = "english"
    game.score = 123
    game.level = 3
    game.combo = 4
    game.lives = 4
    game.input_text = "typing"
    game.words = []
    game.particles = []
    game.stars = []
    game.shake_timer = gc_mod.INITIAL_SHAKE_TIMER
    game.flash_timer = gc_mod.INITIAL_FLASH_TIMER

    # 触发完整游戏画面绘制
    game.draw_game()
    full_surface = tg_mod.screen.copy()

    # 裁剪输入框局部，聚焦“文字+光标”
    input_area_y = gc_mod.SCREEN_HEIGHT - (gc_mod.INPUT_PANEL_HEIGHT + gc_mod.KEYBOARD_PANEL_HEIGHT)
    box_x = gc_mod.INPUT_BOX_X
    box_y = input_area_y + gc_mod.INPUT_BOX_Y_OFFSET
    box_w = gc_mod.SCREEN_WIDTH - gc_mod.INPUT_BOX_WIDTH_MARGIN
    box_h = gc_mod.INPUT_BOX_HEIGHT

    pad = max(6, int(round(8 * scale)))
    crop_rect = pygame.Rect(
        max(0, box_x - pad),
        max(0, box_y - pad),
        min(gc_mod.SCREEN_WIDTH - max(0, box_x - pad), box_w + pad * 2),
        min(gc_mod.SCREEN_HEIGHT - max(0, box_y - pad), box_h + pad * 2),
    )

    crop_surface = full_surface.subsurface(crop_rect).copy()

    cursor_rect = game._compute_input_cursor_rect(box_x, box_y, box_h)
    text_top = box_y + gc_mod.INPUT_TEXT_Y_OFFSET
    text_h = tg_mod.font_input.get_height()
    text_bottom = text_top + text_h

    return {
        "scale": scale,
        "full_surface": full_surface,
        "crop_surface": crop_surface,
        "screen_size": (gc_mod.SCREEN_WIDTH, gc_mod.SCREEN_HEIGHT),
        "box_rect": (box_x, box_y, box_w, box_h),
        "cursor_rect": (cursor_rect.x, cursor_rect.y, cursor_rect.w, cursor_rect.h),
        "text_top": text_top,
        "text_bottom": text_bottom,
    }


def _save_image(surface: pygame.Surface, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(path))


def _build_comparison_strip(results: list[dict]):
    panel_w = 520
    panel_h = 180
    header_h = 44
    gap = 12

    total_w = gap + (panel_w + gap) * len(results)
    total_h = header_h + panel_h + gap
    strip = pygame.Surface((total_w, total_h))
    strip.fill((18, 18, 30))

    font = pygame.font.Font(None, 28)
    info_font = pygame.font.Font(None, 22)

    x = gap
    for item in results:
        crop = item["crop_surface"]
        scaled_crop = pygame.transform.smoothscale(crop, (panel_w, panel_h))
        strip.blit(scaled_crop, (x, header_h))

        label = font.render(f"Scale {item['scale']:.1f}x", True, (235, 235, 240))
        strip.blit(label, (x, 10))

        cursor_y = item["cursor_rect"][1]
        cursor_h = item["cursor_rect"][3]
        text_bottom = item["text_bottom"]
        meta = info_font.render(
            f"cursor(y={cursor_y}, h={cursor_h}) text_bottom={text_bottom}",
            True,
            (170, 190, 230),
        )
        strip.blit(meta, (x + 160, 14))

        x += panel_w + gap

    return strip


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    try:
        for scale in SCALES:
            result = _render_single_scale(scale)
            results.append(result)

            scale_tag = f"{scale:.1f}x"
            _save_image(result["full_surface"], OUTPUT_DIR / f"cursor_full_{scale_tag}.png")
            _save_image(result["crop_surface"], OUTPUT_DIR / f"cursor_crop_{scale_tag}.png")

        strip = _build_comparison_strip(results)
        _save_image(strip, OUTPUT_DIR / "cursor_crop_comparison_strip.png")

        print("[OK] 可视快照已生成:")
        print(f"  {OUTPUT_DIR}")
        print("\n建议先看：")
        print(f"  {OUTPUT_DIR / 'cursor_crop_comparison_strip.png'}")
    finally:
        os.environ.pop("TYPING_GAME_SCALE_RATIO", None)
        pygame.quit()


if __name__ == "__main__":
    main()
