"""Turns photos + words into branded feed image, story image and reel video."""
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FEED_SIZE = (1080, 1350)   # Instagram/Facebook 4:5 portrait - most screen space in feed
STORY_SIZE = (1080, 1920)  # 9:16 for stories and reels

EMBER = (232, 93, 4)
GOLD = (255, 186, 8)
WHITE = (255, 255, 255)
CHARCOAL = (20, 17, 15)

_HEADLINE_FONTS = [ROOT / "fonts/Anton-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
_BODY_FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]

# Fonts can't draw emoji, so strip them from text that goes onto the image.
_EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿️‍]+")


_LOGO = ROOT / "assets/logo.png"


def _logo(height):
    if not _LOGO.exists():
        return None
    logo = Image.open(_LOGO).convert("RGBA")
    return logo.resize((int(logo.width * height / logo.height), height), Image.LANCZOS)


def _paste_logo(img, logo, x, y):
    """Logo with a soft dark halo so it stands out on busy photos."""
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    alpha = logo.getchannel("A").point(lambda a: min(255, a * 2))
    halo.paste((0, 0, 0, 170), (x, y), alpha)
    halo = halo.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), halo)
    img.alpha_composite(logo, (x, y))
    return img.convert("RGB")


def _font(candidates, size):
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def _clean(text):
    return re.sub(r"\s{2,}", " ", _EMOJI.sub("", text)).strip()


def _wrap(draw, text, font, max_w):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _fit(draw, text, fonts, max_w, max_lines, start, minimum):
    size = start
    while size > minimum:
        f = _font(fonts, size)
        lines = _wrap(draw, text, f, max_w)
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 4
    f = _font(fonts, minimum)
    return f, _wrap(draw, text, f, max_w)


def _shade(img):
    """Dark gradient top and bottom so white text always reads."""
    w, h = img.size
    mask = Image.new("L", (1, h))
    for y in range(h):
        t = y / h
        a = 0
        if t < 0.55:
            a = int(200 * (1 - t / 0.55) ** 1.4)
        if t > 0.6:
            a = max(a, int(235 * ((t - 0.6) / 0.4) ** 1.2))
        mask.putpixel((0, y), a)
    mask = mask.resize(img.size)
    dark = Image.new("RGB", img.size, CHARCOAL)
    return Image.composite(dark, img, mask)


def compose(photo, size, headline, sub, brand, handle, top_ratio=0.12, safe_bottom=0.0,
            tag=None, big_logo=False):
    """One branded slide. Headline near top, logo/brand at the bottom.

    big_logo=True makes an end card: large centred logo with the sub line under it.
    """
    img = ImageOps.fit(photo, size, Image.LANCZOS, centering=(0.5, 0.5))
    img = _shade(img)
    d = ImageDraw.Draw(img)
    w, h = size
    margin = 80
    max_w = w - 2 * margin

    headline, sub = _clean(headline), _clean(sub)
    y = int(h * top_ratio)

    if big_logo and _LOGO.exists():
        img = Image.blend(img, Image.new("RGB", size, CHARCOAL), 0.6)  # calm photo so the logo pops
        logo = _logo(int(w * 0.62 * 1059 / 1173))
        ly = int(h * 0.42) - logo.height // 2
        img = _paste_logo(img, logo, (w - logo.width) // 2, ly)
        d = ImageDraw.Draw(img)
        y = ly + logo.height + 60
        for text, f, col in ((sub, _font(_BODY_FONTS, 48), GOLD), (handle, _font(_BODY_FONTS, 40), WHITE)):
            if not text:
                continue
            for line in _wrap(d, text, f, max_w):
                lw = d.textlength(line, font=f)
                d.text(((w - lw) / 2 + 2, y + 2), line, font=f, fill=(0, 0, 0))
                d.text(((w - lw) / 2, y), line, font=f, fill=col, stroke_width=3, stroke_fill=(0, 0, 0))
                y += int(f.size * 1.35)
            y += 20
        d.rectangle([0, h - 14, w, h], fill=EMBER)
        return img

    # Small ember tag line above the headline
    tag_font = _font(_BODY_FONTS, 30)
    tag = _clean(tag or brand).upper()
    tw = d.textlength(tag, font=tag_font)
    d.rounded_rectangle([margin, y, margin + tw + 40, y + 52], radius=26, fill=EMBER)
    d.text((margin + 20, y + 9), tag, font=tag_font, fill=WHITE)
    y += 90

    if headline:
        hf, lines = _fit(d, headline.upper(), _HEADLINE_FONTS, max_w, 4, 130, 60)
        for line in lines:
            # soft ember glow behind text
            glow = Image.new("RGBA", size, (0, 0, 0, 0))
            ImageDraw.Draw(glow).text((margin, y), line, font=hf, fill=EMBER + (200,))
            img.paste(glow.filter(ImageFilter.GaussianBlur(10)), (0, 0), glow.filter(ImageFilter.GaussianBlur(10)))
            d = ImageDraw.Draw(img)
            d.text((margin + 3, y + 4), line, font=hf, fill=(0, 0, 0))
            d.text((margin, y), line, font=hf, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
            y += int(hf.size * 1.12)

    if sub:
        y += 20
        d.rectangle([margin, y, margin + 120, y + 8], fill=GOLD)
        y += 36
        sf, slines = _fit(d, sub, _BODY_FONTS, max_w, 3, 50, 32)
        for line in slines:
            d.text((margin + 2, y + 3), line, font=sf, fill=(0, 0, 0))
            d.text((margin, y), line, font=sf, fill=GOLD, stroke_width=3, stroke_fill=(0, 0, 0))
            y += int(sf.size * 1.3)

    # Logo (or brand name) at the bottom
    bottom = int(h * (1 - safe_bottom)) - 50
    hf2 = _font(_BODY_FONTS, 34)
    logo = _logo(230 if h > 1400 else 200)
    if logo:
        img = _paste_logo(img, logo, margin - 10, bottom - logo.height)
        d = ImageDraw.Draw(img)
        if handle:
            d.text((margin + logo.width + 20, bottom - 50), handle, font=hf2, fill=GOLD)
    else:
        bf = _font(_HEADLINE_FONTS, 64)
        d.text((margin, bottom - 100), brand.upper(), font=bf, fill=WHITE)
        if handle:
            d.text((margin, bottom - 18), handle, font=hf2, fill=GOLD)
    d.rectangle([0, h - 14, w, h], fill=EMBER)
    return img


def render_post(post, photos, cfg, out_dir: Path):
    """Writes feed.jpg, story.jpg, reel.mp4 into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    brand = cfg["brand"]["name"]
    handle = cfg["brand"].get("handle", "")

    tag = post.get("tag")
    feed = compose(photos[0], FEED_SIZE, post["feed"]["headline"], post["feed"]["sub"], brand, handle, tag=tag)
    feed.save(out_dir / "feed.jpg", quality=92)

    # Stories: keep text clear of the top profile bar and bottom reply box.
    story = compose(photos[1 % len(photos)], STORY_SIZE, post["story"]["headline"], post["story"]["sub"],
                    brand, handle, top_ratio=0.16, safe_bottom=0.1, tag=tag)
    story.save(out_dir / "story.jpg", quality=92)

    slide_paths = []
    for i, s in enumerate(post["reel"]["slides"]):
        # Reels: Instagram puts caption & buttons on the bottom ~20%.
        last = i == len(post["reel"]["slides"]) - 1
        slide = compose(photos[(i + 2) % len(photos)], STORY_SIZE, s["headline"], s["sub"], brand, handle,
                        top_ratio=0.18, safe_bottom=0.2, tag=tag, big_logo=last)
        p = out_dir / f"reel_slide_{i + 1}.jpg"
        slide.save(p, quality=92)
        slide_paths.append(p)
    make_reel(slide_paths, out_dir / "reel.mp4", music_dir=ROOT / "music")


def make_reel(slides, out_path: Path, seconds_per_slide=4.0, fade=0.6, music_dir: Path = None):
    """Slow zoom on each slide + crossfades. Uses music/*.mp3 if present, else a silent track."""
    fps = 30
    frames = int(seconds_per_slide * fps)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for s in slides:
        cmd += ["-loop", "1", "-t", str(seconds_per_slide), "-i", str(s)]

    music = sorted(music_dir.glob("*.mp3")) if music_dir and music_dir.exists() else []
    total = len(slides) * seconds_per_slide - (len(slides) - 1) * fade
    if music:
        import random
        cmd += ["-i", str(random.choice(music))]
    else:
        cmd += ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    audio_idx = len(slides)

    parts = []
    for i in range(len(slides)):
        zoom_in = i % 2 == 0
        z = "min(zoom+0.0006,1.07)" if zoom_in else "if(eq(on,0),1.07,max(zoom-0.0006,1.0))"
        parts.append(f"[{i}:v]scale=2160:3840,zoompan=z='{z}':d={frames}:"
                     f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps},"
                     f"format=yuv420p,setsar=1[v{i}]")
    last = "v0"
    for i in range(1, len(slides)):
        offset = i * (seconds_per_slide - fade)
        parts.append(f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={offset}[x{i}]")
        last = f"x{i}"
    parts.append(f"[{audio_idx}:a]atrim=0:{total},afade=t=out:st={total - 1}:d=1[a]")

    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-r", str(fps), "-movflags", "+faststart",
            "-t", str(total), str(out_path)]
    subprocess.run(cmd, check=True)
