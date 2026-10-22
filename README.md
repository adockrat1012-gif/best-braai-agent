# 🔥 Best Braai: Social Media Agent

Posts to **Instagram and Facebook every second day**, fully automatically:

| Each posting day | What it is |
|---|---|
| **Feed post** | 1080×1350 branded image + caption + hashtags |
| **Story** | 1080×1920 branded image with your call-to-action |
| **Reel** | ~11 s vertical video: 3 slides (hook → braai tip → your brand) with slow zoom & fades |

You never upload anything. The agent picks a free braai photo, adds your branding and writes the caption itself.

## What it posts about

* **Weekends:** Friday *"Happy weekend, ready to braai?"*, Saturday *"Saturday = Braai Day"*, Sunday *"Sunday Funday = Braai Day!"*
* **SA public holidays:** Heritage Day / National Braai Day, Freedom Day, Youth Day, Women's Day, Easter, Christmas, New Year, Mother's & Father's Day and more. It posts on the day, or the day before when the holiday falls between posting days.
* **SA seasons:** summer (sosaties, pool braais), autumn (cool evenings, potjie), winter (potjiekos, rooikrans, braai all year), spring (braai season is back).
* **Charcoal & wood:** charcoal vs wood, kameeldoring/rooikrans/sekelbos, the hand test, white coals, no lighter fluid, two-zone fire.
* **Month-end payday weekends.**

See the plan for the next 2 months: `python -m braai_agent plan --days 60`

## Free photos

Searched in this order, never reusing a photo:
1. **Pexels** (free API key, commercial use OK, no credit needed)
2. **Pixabay** (free API key, optional)
3. **Openverse** (no key needed; credit is added to the caption automatically)
4. If everything fails, it **draws its own fire artwork**, so a post is never missed.

## Setup (one time, about 30 minutes)

### 1. Put this folder on GitHub
Create a free account at github.com → **New repository** → name it `best-braai-agent` → **Public** → upload these files.
(It must be public: Instagram downloads the images from GitHub.)

### 2. Get a free Pexels key (recommended)
pexels.com/api → sign up → copy your API key.

### 3. Connect Instagram & Facebook (Meta)
1. Your Instagram must be a **Business or Creator** account, **linked to your Facebook Page**
   (Instagram app → Settings → Account type / Linked accounts).
2. Go to **developers.facebook.com** → My Apps → **Create App** → type **Business**.
3. Open **Tools → Graph API Explorer**, select your app, click **Generate Access Token** and tick:
   `pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish, business_management`
4. Make the token long-lived: **Tools → Access Token Debugger** → paste it → **Extend Access Token**.
5. Back in Graph API Explorer, with the long-lived token, run `me/accounts`.
   Copy your Page's **`access_token`** (this Page token does not expire) and its **`id`** (your Page id).
6. Run `<your-page-id>?fields=instagram_business_account` and copy the **`id`** it returns (your Instagram id).

### 4. Add the secrets to GitHub
Repository → **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `PEXELS_API_KEY` | from step 2 |
| `META_ACCESS_TOKEN` | Page access token from step 3.5 |
| `FB_PAGE_ID` | Page id from step 3.5 |
| `IG_USER_ID` | Instagram id from step 3.6 |
| `PIXABAY_API_KEY` | optional |

### 5. Edit `config.yaml`
Set your real Instagram handle, call-to-action text and the first posting date.

### 6. Test it
GitHub → **Actions** → *Braai social posts* → **Run workflow** → tick **force** and **dry_run** → Run.
Open the run to see the generated images (under *Artifacts*). Happy with them? Run again with only **force** ticked to post for real.

After that it runs by itself every day at **17:17 SA time** and posts every second day.

## Optional extras
* **Music on reels:** drop royalty-free `.mp3` files into the `music/` folder (e.g. from pixabay.com/music); one is chosen at random. Without music, reels have a silent track.
* **Your own font:** the workflow downloads the free *Anton* poster font automatically.
* **Change frequency:** `every_n_days` in `config.yaml`.
* **Only Instagram / only Facebook:** set `platforms` in `config.yaml`.

## Run on your own computer
```bash
pip install -r requirements.txt          # also needs ffmpeg installed
python -m braai_agent generate --force   # creates posts/<today>/feed.jpg, story.jpg, reel.mp4, caption.txt
python -m braai_agent publish posts/<today> --dry-run
```
