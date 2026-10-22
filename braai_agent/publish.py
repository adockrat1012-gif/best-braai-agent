"""Publishes to Instagram and Facebook via Meta's official Graph API.

Needs (as environment variables / GitHub secrets):
  META_ACCESS_TOKEN  long-lived Page access token (covers the Page and its linked Instagram)
  FB_PAGE_ID         Facebook Page id          (leave empty to skip Facebook)
  IG_USER_ID         Instagram business id     (leave empty to skip Instagram)
Images must be at a public URL (Instagram fetches them). Videos are uploaded directly.
"""
import os
import time
from pathlib import Path

import requests

API = "v21.0"
GRAPH = f"https://graph.facebook.com/{API}"


class Meta:
    def __init__(self):
        self.token = os.environ["META_ACCESS_TOKEN"]
        self.page = os.getenv("FB_PAGE_ID", "").strip()
        self.ig = os.getenv("IG_USER_ID", "").strip()

    def _call(self, method, path, **params):
        url = path if path.startswith("http") else f"{GRAPH}/{path}"
        r = requests.request(method, url, data=params if method == "POST" else None,
                             params=None if method == "POST" else params,
                             headers={"Authorization": f"Bearer {self.token}"}, timeout=120)
        body = r.json() if r.content else {}
        if r.status_code >= 400 or "error" in body:
            raise RuntimeError(f"{method} {path}: {body.get('error', body)}")
        return body

    def _upload(self, upload_url, video: Path):
        data = video.read_bytes()
        r = requests.post(upload_url, data=data, timeout=600, headers={
            "Authorization": f"OAuth {self.token}", "offset": "0", "file_size": str(len(data))})
        if r.status_code >= 400:
            raise RuntimeError(f"video upload failed: {r.text}")

    # ---------------- Instagram ----------------
    def _ig_wait(self, container, minutes=10):
        for _ in range(minutes * 6):
            status = self._call("GET", container, fields="status_code").get("status_code")
            if status == "FINISHED":
                return
            if status in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Instagram processing {status} for {container}")
            time.sleep(10)
        raise TimeoutError("Instagram media still processing")

    def _ig_publish(self, container):
        self._ig_wait(container)
        return self._call("POST", f"{self.ig}/media_publish", creation_id=container)["id"]

    def ig_feed(self, image_url, caption):
        c = self._call("POST", f"{self.ig}/media", image_url=image_url, caption=caption)["id"]
        return self._ig_publish(c)

    def ig_story(self, image_url):
        c = self._call("POST", f"{self.ig}/media", image_url=image_url, media_type="STORIES")["id"]
        return self._ig_publish(c)

    def ig_reel(self, video: Path, caption):
        c = self._call("POST", f"{self.ig}/media", media_type="REELS", upload_type="resumable",
                       caption=caption, share_to_feed="true")
        self._upload(c["uri"], video)
        return self._ig_publish(c["id"])

    # ---------------- Facebook Page ----------------
    def fb_feed(self, image_url, caption):
        return self._call("POST", f"{self.page}/photos", url=image_url, message=caption)["id"]

    def fb_story(self, image_url):
        photo = self._call("POST", f"{self.page}/photos", url=image_url, published="false")["id"]
        return self._call("POST", f"{self.page}/photo_stories", photo_id=photo).get("post_id", photo)

    def fb_reel(self, video: Path, caption):
        vid = self._call("POST", f"{self.page}/video_reels", upload_phase="start")["video_id"]
        self._upload(f"https://rupload.facebook.com/video-upload/{API}/{vid}", video)
        self._call("POST", f"{self.page}/video_reels", upload_phase="finish", video_id=vid,
                   video_state="PUBLISHED", description=caption)
        return vid


def publish(post_dir: Path, base_url: str, caption: str, platforms: dict, dry_run=False):
    feed_url, story_url = f"{base_url}/feed.jpg", f"{base_url}/story.jpg"
    reel = post_dir / "reel.mp4"
    steps = []
    if platforms.get("instagram", True):
        steps += [("instagram feed", lambda m: m.ig_feed(feed_url, caption)),
                  ("instagram story", lambda m: m.ig_story(story_url)),
                  ("instagram reel", lambda m: m.ig_reel(reel, caption))]
    if platforms.get("facebook", True):
        steps += [("facebook feed", lambda m: m.fb_feed(feed_url, caption)),
                  ("facebook story", lambda m: m.fb_story(story_url)),
                  ("facebook reel", lambda m: m.fb_reel(reel, caption))]

    if dry_run:
        for name, _ in steps:
            print(f"  [dry-run] would publish {name}")
        print(f"  feed image: {feed_url}\n  story image: {story_url}")
        return {name: "dry-run" for name, _ in steps}

    meta = Meta()
    results = {}
    for name, fn in steps:
        if name.startswith("instagram") and not meta.ig or name.startswith("facebook") and not meta.page:
            results[name] = "skipped (no id configured)"
            continue
        try:
            results[name] = f"ok {fn(meta)}"
        except Exception as e:  # noqa: BLE001 - keep going with the other platforms
            results[name] = f"FAILED {e}"
        print(f"  {name}: {results[name]}")
    return results
