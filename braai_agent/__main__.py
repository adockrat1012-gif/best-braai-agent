"""Best Braai social media agent.

  python -m braai_agent generate [--date 2026-10-23] [--force]
  python -m braai_agent publish posts/2026-10-23 [--dry-run]
  python -m braai_agent plan --days 30
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import content, images, publish, render

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"


def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def today_sa():
    return datetime.now(ZoneInfo("Africa/Johannesburg")).date()


def is_posting_day(d: date, cfg) -> bool:
    start = date.fromisoformat(str(cfg["schedule"]["start_date"]))
    every = int(cfg["schedule"].get("every_n_days", 2))
    return (d - start).days % every == 0


def set_output(**kw):
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for k, v in kw.items():
                f.write(f"{k}={v}\n")


def cmd_generate(args, cfg):
    d = date.fromisoformat(args.date) if args.date else today_sa()
    if not args.force and not is_posting_day(d, cfg):
        print(f"{d}: not a posting day (posting every {cfg['schedule'].get('every_n_days', 2)} days).")
        set_output(should_post="false")
        return
    out = POSTS / d.isoformat()
    if (out / "published.json").exists() and not args.force:
        print(f"{d}: already published.")
        set_output(should_post="false")
        return

    post = content.build_post(d, cfg)
    print(f"{d}: theme={post['theme']} season={post['season']}")
    print(f"  headline: {post['feed']['headline']}")
    photos = images.fetch_images(post["queries"], 3, POSTS / "used_images.json", seed=d.toordinal())
    credits = sorted({c for _, c in photos if c})
    cc_credits = [c for c in credits if "(CC" in c]  # Creative Commons photos need attribution
    if cc_credits:
        post["caption"] += "\n\n📸 " + "; ".join(cc_credits)
    post["credits"] = credits

    render.render_post(post, [p for p, _ in photos], cfg, out)
    (out / "post.json").write_text(json.dumps(post, indent=2, ensure_ascii=False))
    (out / "caption.txt").write_text(post["caption"])
    for f in out.glob("reel_slide_*.jpg"):
        f.unlink()
    print(f"  created {out.relative_to(ROOT)}/ feed.jpg story.jpg reel.mp4")
    set_output(should_post="true", post_dir=str(out.relative_to(ROOT)))


def media_base_url(post_dir: Path, cfg):
    base = os.getenv("MEDIA_BASE_URL") or cfg.get("media_base_url")
    rel = post_dir.resolve().relative_to(ROOT).as_posix()
    if base:
        return f"{base.rstrip('/')}/{rel}"
    repo = os.getenv("GITHUB_REPOSITORY")
    branch = os.getenv("GITHUB_REF_NAME", "main")
    if not repo:
        sys.exit("Set MEDIA_BASE_URL (or run in GitHub Actions) so Instagram can fetch the images.")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel}"


def cmd_publish(args, cfg):
    post_dir = Path(args.post_dir)
    if not post_dir.is_absolute():
        post_dir = ROOT / post_dir
    caption = (post_dir / "caption.txt").read_text()
    results = publish.publish(post_dir, media_base_url(post_dir, cfg), caption,
                              cfg.get("platforms", {}), dry_run=args.dry_run)
    if args.dry_run:
        return
    (post_dir / "published.json").write_text(json.dumps(results, indent=2))
    if not any(v.startswith("ok") for v in results.values()):
        sys.exit("Nothing was published. See errors above.")


def cmd_plan(args, cfg):
    d = date.fromisoformat(args.date) if args.date else today_sa()
    for i in range(args.days):
        day = d + timedelta(days=i)
        if is_posting_day(day, cfg):
            p = content.build_post(day, cfg)
            print(f"{day} {day:%a}  [{p['season']:6}] {p['theme']:22} {p['feed']['headline']}")


def main():
    ap = argparse.ArgumentParser(prog="braai_agent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--date")
    g.add_argument("--force", action="store_true", help="generate even if not a posting day")
    p = sub.add_parser("publish")
    p.add_argument("post_dir")
    p.add_argument("--dry-run", action="store_true")
    pl = sub.add_parser("plan")
    pl.add_argument("--date")
    pl.add_argument("--days", type=int, default=30)
    args = ap.parse_args()
    cfg = load_config()
    {"generate": cmd_generate, "publish": cmd_publish, "plan": cmd_plan}[args.cmd](args, cfg)


if __name__ == "__main__":
    main()
