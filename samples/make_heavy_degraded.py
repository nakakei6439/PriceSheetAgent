"""既存の *_degraded.pdf をさらに劣化させ *_degraded_heavy.pdf を生成する.

目的: Document Intelligence の信頼度を CONFIDENCE_FLOOR (0.6) 未満まで落とし,
agent.py の GPT-4o Vision フォールバック + 自己検証ループをデモで発火させる.

"参照リレー" (Excel→PDF→印刷→スキャン→再印刷→再スキャン...) で蓄積する劣化を模擬:
低解像度化 / ぼけ / コントラスト低下 / センサノイズ / 微小回転 / 低品質JPEG多重圧縮.

依存: Pillow, pdf2image (poppler). numpy 不要.
"""
from __future__ import annotations

import hashlib
import io
import random
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_bytes

SAMPLES = Path(__file__).resolve().parent
NAMES = ["ja_invoice_a", "ja_invoice_b", "en_invoice_a", "en_invoice_b"]

# 劣化パラメータ (強め). 必要なら調整.
import os

# 既定値は実測でチューニング済み: Document Intelligence の avg_conf を
# CONFIDENCE_FLOOR (0.6) 未満まで落としつつ, GPT-4o Vision はおおむね読める領域.
# これにより agent.py のフォールバック (DI低信頼→Vision) と
# 自己検証ループ (verify_math 失敗→Vision 再抽出) がデモで発火する.
RENDER_DPI = int(os.environ.get("HD_DPI", 140))
DOWNSCALE = float(os.environ.get("HD_DOWNSCALE", 0.36))   # いったん縮小 → 等倍へ戻す (解像度損失)
BLUR_RADIUS = float(os.environ.get("HD_BLUR", 1.85))
CONTRAST = float(os.environ.get("HD_CONTRAST", 0.66))     # かすれ印刷
BRIGHTNESS = float(os.environ.get("HD_BRIGHT", 1.10))
NOISE_SIGMA = int(os.environ.get("HD_NOISE", 30))         # スキャナ/センサノイズ
NOISE_ALPHA = float(os.environ.get("HD_NOISE_A", 0.24))
ROTATE_DEG = float(os.environ.get("HD_ROT", 2.2))         # 手スキャン/撮影の傾き
JPEG_ROUNDS = int(os.environ.get("HD_JPEG_ROUNDS", 3))    # 低品質JPEG多重圧縮
JPEG_QUALITY = int(os.environ.get("HD_JPEG_Q", 17))


def degrade(img: Image.Image, seed: int) -> Image.Image:
    random.seed(seed)
    img = img.convert("L")  # グレースケール (白黒コピー機を模擬)

    w, h = img.size
    small = img.resize((max(1, int(w * DOWNSCALE)), max(1, int(h * DOWNSCALE))), Image.BILINEAR)
    img = small.resize((w, h), Image.BILINEAR)

    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    img = ImageEnhance.Contrast(img).enhance(CONTRAST)
    img = ImageEnhance.Brightness(img).enhance(BRIGHTNESS)

    noise = Image.effect_noise(img.size, NOISE_SIGMA)
    img = Image.blend(img, noise, NOISE_ALPHA)

    angle = random.uniform(-ROTATE_DEG, ROTATE_DEG)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=235)

    for _ in range(JPEG_ROUNDS):
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=JPEG_QUALITY)
        buf.seek(0)
        img = Image.open(buf).convert("L")

    return img.convert("RGB")


def process(name: str) -> Path:
    src = SAMPLES / f"{name}_degraded.pdf"
    if not src.exists():
        raise FileNotFoundError(src)
    pages = convert_from_bytes(src.read_bytes(), dpi=RENDER_DPI)
    # 決定的シード (Python の hash() はプロセス毎にランダム化されるため使わない)
    base_seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:4], "big")
    degraded = [degrade(p, seed=base_seed + i) for i, p in enumerate(pages)]
    out = SAMPLES / f"{name}_degraded_heavy.pdf"
    head, *rest = degraded
    head.save(out, format="PDF", save_all=True, append_images=rest, resolution=RENDER_DPI)
    return out


if __name__ == "__main__":
    targets = sys.argv[1:] or NAMES
    for n in targets:
        out = process(n)
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)")
