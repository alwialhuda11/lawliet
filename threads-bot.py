#!/usr/bin/env python3
"""
Threads Affiliate Bot v3 — ADAPTED for Windows + multi-account ready
Auto Comment with Shopee Affiliate Links  (DRY-RUN safe by default)

EDIT:
  - YOUR_USERNAME  : username Threads lu (tanpa @)
  - AFFILIATE_DB   : isi dengan link affiliate asli (bukan "LINK_ID_x")
  - CHROME_PORT    : port remote-debugging Chrome (9222 default; 9223.. utk akun ke-2 dst)
  - DRY_RUN        : True = hanya scan+analisis+tampilkan komen, TIDAK kirim.
                     Set False BARU beneran posting.
"""

import json
import requests
import websocket
import time
import datetime
import random
import sys
import os

# ==========================================
# CONFIGURATION
# ==========================================

CHROME_HOST = os.environ.get("CHROME_HOST", "localhost")
CHROME_PORT = int(os.environ.get("CHROME_PORT", "9222"))

# Cuma comment post <= N hari (hindari post basi yg jarang dibuka).
MAX_AGE_DAYS = int(os.environ.get("MAX_AGE_DAYS", "60"))

DRY_RUN = False  # << LIVE: beneran kirim komen

YOUR_USERNAME = "user529362927"  # << username Threads lu

# Link affiliate asli (bisa full URL atau short code s.shopee.co.id/XXXX).
AFFILIATE_DB = {
    "skincare": {
        "moisturizer": ["https://s.shopee.co.id/4AyPP83wIq", "https://s.shopee.co.id/LlgqDagHA", "https://s.shopee.co.id/80B7yO73Wi", "https://s.shopee.co.id/6ffkNxsUIC", "https://s.shopee.co.id/AAFcYRZtaK"],
        "retinol": ["https://s.shopee.co.id/3ViicFoNX9", "https://s.shopee.co.id/20tupbkFWv", "https://s.shopee.co.id/4AyPPdNB46", "https://s.shopee.co.id/5VTn0706iG", "https://s.shopee.co.id/5fnDCT9oJ9"],
        "sunscreen": ["https://s.shopee.co.id/9zwCMSAqtk", "https://s.shopee.co.id/1gH4RC9gJn", "https://s.shopee.co.id/2qT1pM9AQL", "https://s.shopee.co.id/1gH4REZcET", "https://s.shopee.co.id/80B7yt2RIQ"],
        "acne": ["https://s.shopee.co.id/4qE6D5ZXUW", "https://s.shopee.co.id/2BDL2DbwKO", "https://s.shopee.co.id/3ViicgiLwW", "https://s.shopee.co.id/2BDL2FnIeZ", "https://s.shopee.co.id/2VqBQtg4Dg"]
    },
    "makeup": {
        "liptint": ["https://s.shopee.co.id/4fug0uCO48", "https://s.shopee.co.id/6L2tzzYzbs", "https://s.shopee.co.id/30mS1sV7ho", "https://s.shopee.co.id/8V7OZzvpGi", "https://s.shopee.co.id/8pkEycXfnd"],
        "cushion": ["https://s.shopee.co.id/W573MSva4", "https://s.shopee.co.id/40ezDo7IHJ", "https://s.shopee.co.id/6ffkOivm9Q", "https://s.shopee.co.id/8fQomPo6ML", "https://s.shopee.co.id/1gH4RYs4Ya"],
        "setting_spray": ["https://s.shopee.co.id/2g9bdRDNIW", "https://s.shopee.co.id/2qT1plU4ZM", "https://s.shopee.co.id/9KgVZjHmNu", "https://s.shopee.co.id/AUsSxts72w", "https://s.shopee.co.id/2qT1ppK8f2"]
    },
    "parfum": {
        "unisex": ["https://s.shopee.co.id/4VbFovGd5V", "https://s.shopee.co.id/3g28pPWb57", "https://s.shopee.co.id/20tuqMq0oa", "https://s.shopee.co.id/1LeE3AEQ5K", "https://s.shopee.co.id/6L2u0MUVw8"],
        "body_mist": ["https://s.shopee.co.id/5VTn0t1PUy", "https://s.shopee.co.id/2BDL2jaDeX", "https://s.shopee.co.id/30mS2JVpoW", "https://s.shopee.co.id/2qT1q2106r", "https://s.shopee.co.id/2BDL2pq57g"]
    }
}

KEYWORDS = {
    "skincare": ["skincare", "serum", "moisturizer", "sunscreen", "retinol", "cream",
                  "toner", "cleanser", "acne", "jerawat", "glowing", "bruntusan",
                  "kulit", "face wash", "mask", "pelembab", "tabir surya", "cuci muka"],
    "makeup": ["makeup", "lipstick", "foundation", "mascara", "eyeshadow", "blush",
               "bedak", "cushion", "lip tint", "cosmetics", "lipstik", "concealer",
               "primer", "base makeup", "make up"],
    "parfum": ["parfum", "perfume", "fragrance", "wangi", "cologne", "body mist",
               "eau de", "aroma", "pengharum", "bau badan"]
}


# ==========================================
# CDP FUNCTIONS
# ==========================================

def get_ws_url():
    """Get WebSocket URL — prefer tab posting (/post/), lalu threads.net, lalu pertama."""
    resp = requests.get(f"http://{CHROME_HOST}:{CHROME_PORT}/json", timeout=10)
    pages = resp.json()
    if not pages:
        raise Exception("Chrome tidak berjalan di port %s! Buka dengan remote debugging." % CHROME_PORT)
    for p in pages:
        if "/post/" in p.get("url", ""):
            return p["webSocketDebuggerUrl"]
    for p in pages:
        if "threads.net" in p.get("url", ""):
            return p["webSocketDebuggerUrl"]
    return pages[0]["webSocketDebuggerUrl"]


def cdp_eval(expr, timeout=30):
    ws = websocket.create_connection(get_ws_url(), timeout=timeout)
    ws.send(json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": expr, "returnByValue": True, "awaitPromise": True}
    }))
    msg = json.loads(ws.recv())
    ws.close()
    return msg.get("result", {}).get("result", {}).get("value")


def cdp_navigate(url, timeout=30):
    ws = websocket.create_connection(get_ws_url(), timeout=timeout)
    ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
    json.loads(ws.recv())
    ws.close()


def click_at(x, y):
    ws = websocket.create_connection(get_ws_url(), timeout=30)
    ws.send(json.dumps({"id": 1, "method": "Input.dispatchMouseEvent",
                        "params": {"type": "mouseMoved", "x": x, "y": y}}))
    json.loads(ws.recv())
    time.sleep(0.2)
    ws.send(json.dumps({"id": 2, "method": "Input.dispatchMouseEvent",
                        "params": {"type": "mousePressed", "x": x, "y": y,
                                   "button": "left", "clickCount": 1}}))
    json.loads(ws.recv())
    time.sleep(0.1)
    ws.send(json.dumps({"id": 3, "method": "Input.dispatchMouseEvent",
                        "params": {"type": "mouseReleased", "x": x, "y": y,
                                   "button": "left", "clickCount": 1}}))
    json.loads(ws.recv())
    ws.close()


def insert_text(text):
    expr = (
        "(() => {"
        "  const ce = document.querySelector('[role=\"dialog\"] [contenteditable=\"true\"]') || document.querySelector('[contenteditable=\"true\"]');"
        "  if (!ce) return 'NO_EDITOR';"
        "  ce.focus();"
        "  const parts = " + json.dumps(text) + ".split('\\n');"
        "  document.execCommand('insertText', false, parts[0]);"
        "  for (let i = 1; i < parts.length; i++) {"
        "    document.execCommand('insertText', false, (parts[i].length ? ' ' + parts[i] : ' '));"
        "  }"
        "  return 'OK';"
        "})()"
    )
    return cdp_eval(expr, 15)


# ==========================================
# BOT FUNCTIONS
# ==========================================

def final_link(affiliate_link):
    s = str(affiliate_link)
    return s if s.startswith("http") else "https://s.shopee.co.id/" + s


SEARCH_QUERIES = ["skincare", "jerawat", "bruntusan", "makeup", "parfum", "glowing", "rekomendasi skincare"]
LAST_QUERY = ""


def scan_threads():
    global LAST_QUERY
    print("[1/5] Scanning Threads (search mode)...")
    q = random.choice(SEARCH_QUERIES)
    LAST_QUERY = q
    print(f"    query: {q}")
    cdp_navigate("https://www.threads.net/search?q=" + requests.utils.quote(q))
    time.sleep(8)
    # klik tab Top / Teratas (post viral/populer)
    tab = cdp_eval("""(() => {
        const els = document.querySelectorAll('a, div[role="tab"], span, button');
        for (const e of els) {
            const tx = (e.textContent||'').trim().toLowerCase();
            if (tx === 'top' || tx === 'teratas') { e.click(); return tx; }
        }
        return 'no-tab';
    })()""", 10)
    print(f"    tab: {tab}")
    time.sleep(3)
    for _ in range(4):
        cdp_eval("window.scrollBy(0, 1000)")
        time.sleep(2)
    raw = cdp_eval(r"""
        (() => {
            const out = [];
            const seen = new Set();
            document.querySelectorAll('a[href*="/post/"]').forEach(a => {
                const m = a.href.match(/\/post\/([^/?#]+)/);
                if (!m) return;
                const pid = m[1];
                if (seen.has(pid)) return;
                seen.add(pid);
                let ctx = a.closest('article');
                if (!ctx) { let p = a.parentElement; for (let i = 0; i < 6 && p; i++) { if (p.querySelector('time')) { ctx = p; break; } p = p.parentElement; } }
                if (!ctx) ctx = a.parentElement;
                const times = Array.from(document.querySelectorAll('time')).filter(t => ctx && ctx.contains(t));
                const dt = times.length ? times[0].getAttribute('datetime') : '';
                out.push({ url: a.href.split('#')[0], dt });
            });
            return JSON.stringify(out.slice(0, 30));
        })()
    """, 15)
    items = json.loads(raw) if raw else []
    posted = load_posted()
    now = datetime.datetime.now(datetime.timezone.utc)
    keep = []
    skip_old = 0
    skip_posted = 0
    for it in items:
        url = it.get("url", "")
        if not url:
            continue
        if url in posted:
            skip_posted += 1
            continue
        dt = it.get("dt", "")
        age = None
        if dt:
            try:
                d = datetime.datetime.fromisoformat(dt.replace("Z", "+00:00"))
                age = (now - d).days
            except Exception:
                age = None
        if age is not None and age > MAX_AGE_DAYS:
            skip_old += 1
            continue
        keep.append(url)
    if skip_old:
        print(f"    Skip {skip_old} post > {MAX_AGE_DAYS} hari (basi)")
    if skip_posted:
        print(f"    Skip {skip_posted} post sudah pernah di-comment")
    print(f"    Found {len(keep)} posts (<= {MAX_AGE_DAYS} hari)")
    return keep


def analyze_post(url):
    cdp_navigate(url)
    time.sleep(4)
    text = cdp_eval("document.body.innerText", 30)
    if not text:
        return None
    if YOUR_USERNAME and YOUR_USERNAME.lower() in text.lower():
        return None
    lines = text.split("\n")
    post_content = ""
    for i, line in enumerate(lines):
        if line.strip().startswith('@') and len(line.strip()) > 3:
            for k in range(i + 1, min(i + 8, len(lines))):
                if len(lines[k].strip()) > 10:
                    post_content = lines[k].strip()
                    break
            break
    # fallback ekstraksi isi post (Threads SPA)
    if not post_content:
        candidates = [l.strip() for l in lines if len(l.strip()) > 15 and not l.strip().startswith('@')]
        if candidates:
            post_content = max(candidates, key=len)
    if not post_content:
        post_content = text.strip()[:200]
    content_lower = post_content.lower()
    detected_category = None
    detected_subcategory = None
    for category, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in content_lower:
                detected_category = category
                if category == "skincare":
                    if any(w in content_lower for w in ["moisturizer", "pelembab", "moistur"]):
                        detected_subcategory = "moisturizer"
                    elif any(w in content_lower for w in ["retinol", "retinoid"]):
                        detected_subcategory = "retinol"
                    elif any(w in content_lower for w in ["sunscreen", "tabir surya", "spf"]):
                        detected_subcategory = "sunscreen"
                    elif any(w in content_lower for w in ["acne", "jerawat", "bruntusan", "bekas"]):
                        detected_subcategory = "acne"
                    else:
                        detected_subcategory = "moisturizer"
                elif category == "makeup":
                    if any(w in content_lower for w in ["lip", "bibir"]):
                        detected_subcategory = "liptint"
                    elif any(w in content_lower for w in ["cushion", "foundation", "bedak"]):
                        detected_subcategory = "cushion"
                    elif any(w in content_lower for w in ["setting", "spray", "primer"]):
                        detected_subcategory = "setting_spray"
                    else:
                        detected_subcategory = "liptint"
                elif category == "parfum":
                    if any(w in content_lower for w in ["body mist", "mist"]):
                        detected_subcategory = "body_mist"
                    else:
                        detected_subcategory = "unisex"
                break
        if detected_category:
            break
    # fallback: pakai query search sebagai penentu kategori
    if not detected_category and LAST_QUERY:
        ql = LAST_QUERY.lower()
        if any(k in ql for k in KEYWORDS["skincare"]):
            detected_category = "skincare"; detected_subcategory = "moisturizer"
        elif any(k in ql for k in KEYWORDS["makeup"]):
            detected_category = "makeup"; detected_subcategory = "liptint"
        elif any(k in ql for k in KEYWORDS["parfum"]):
            detected_category = "parfum"; detected_subcategory = "unisex"
    if not detected_category:
        return None
    return {"url": url, "content": post_content, "category": detected_category, "subcategory": detected_subcategory}


def get_affiliate_link(category, subcategory=None):
    if category not in AFFILIATE_DB:
        return None
    if subcategory and subcategory in AFFILIATE_DB[category]:
        links = AFFILIATE_DB[category][subcategory]
        if links:
            return random.choice(links)
    all_links = []
    for links in AFFILIATE_DB[category].values():
        all_links.extend(links)
    return random.choice(all_links) if all_links else None


OPENERS = ["bestie!", "sis!", "guys!", "hallo!", "bestiee!", "yuk simak!", "hallo bestie!"]
SKINCARE_BODIES = [
    "produk ini emang best sih, hasilnya keliatan banget. harganya juga terjangkau bgt",
    "worth it banget sih, kulit jadi lebih halus. cocok buat kantong pelajar",
    "auto repurchase nih, hasilnya nyata dan harganya student friendly",
    "real talk, ini ngebantu banget. murah tapi kualitas gak kalengan",
    "udah coba sendiri, hasilnya keliatan. harganya ramah di kantong bgt",
]
MAKEUP_BODIES = [
    "ini sih auto repurchase, worth it banget. coba deh bestie",
    "bagus bgt hasilnya, harganya murah lagi. auto checkout sih ini",
    "worth it sih, finish-nya rapi dan harganya pelajar banget",
    "real rekomendasi, kualitas oke harganya gak bikin bokek",
]
PARFUM_BODIES = [
    "wanginya tahan lama bgt, harganya juga ramah di kantong",
    "suka banget sama wanginya, harganya murah lagi. auto checkout",
    "worth it sih, wanginya awet dan harganya pelajar friendly",
    "ini sih bikin pede, wanginya tahan lama harganya terjangkau",
]
CLOSERS = ["", "✨", "🤍", "recommended bgt!", "wajib coba sih!", "jangan lewatkan!"]

def _bodies_for(category):
    c = (category or "skincare").lower()
    if c.startswith("makeup"): return MAKEUP_BODIES
    if c.startswith("parfum"): return PARFUM_BODIES
    return SKINCARE_BODIES

LAST_COMMENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_comment.txt")
POSTED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted.txt")

def load_posted():
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    except Exception:
        return set()

def save_posted(url):
    try:
        with open(POSTED_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception:
        pass

def generate_comment(fl, category):
    bodies = _bodies_for(category)
    last = ""
    try:
        with open(LAST_COMMENT_FILE, "r", encoding="utf-8") as f:
            last = f.read().strip()
    except Exception:
        last = ""
    for _ in range(10):
        opener = random.choice(OPENERS)
        body = random.choice(bodies)
        closer = random.choice(CLOSERS)
        text = opener + " " + body
        if closer:
            text += " " + closer
        text += "\n\n" + fl
        if text != last:
            try:
                with open(LAST_COMMENT_FILE, "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception:
                pass
            return text
    return OPENERS[0] + " " + bodies[0] + "\n\n" + fl


def post_comment(post_info, affiliate_link):
    fl = final_link(affiliate_link)
    url = post_info["url"]
    cdp_navigate(url)
    time.sleep(6)
    reply_info = cdp_eval("""
        (() => {
            const svgs = document.querySelectorAll('svg[aria-label*="alas"], svg[aria-label*="Reply"]');
            for (const svg of svgs) {
                const rect = svg.getBoundingClientRect();
                if (rect.y > 0 && rect.y < window.innerHeight) {
                    return JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
                }
            }
            return null;
        })()
    """, 15)
    if not reply_info:
        print("    Reply button not found")
        return False
    reply = json.loads(reply_info)
    click_at(int(reply['x']), int(reply['y']))
    print("    Reply clicked!")
    time.sleep(4)
    ce_info = cdp_eval("""
        (() => {
            const ce = document.querySelector('[role="dialog"] [contenteditable="true"]') || document.querySelector('[contenteditable="true"]');
            if (ce) {
                const rect = ce.getBoundingClientRect();
                return JSON.stringify({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
            }
            return null;
        })()
    """, 15)
    if not ce_info:
        print("    Editor not found")
        return False
    category = post_info.get("category", "skincare")
    comment = generate_comment(fl, category)
    insert_text(comment)
    print("    Comment typed!")
    time.sleep(3)

    if DRY_RUN:
        print("    [DRY-RUN] TIDAK mengirim. Komen yg AKAN di-post:")
        print("    >>> " + comment.replace("\n", " \\n "))
        return True

    send_expr = r'''
        (() => {
            function pick(scope) {
                const cands = [];
                scope.querySelectorAll('button, [role="button"]').forEach(b => {
                    if (b.disabled) return;
                    const t = (b.textContent || '').trim().toLowerCase();
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    if (/like|repost|share|follow/.test(aria)) return;
                    if (/\d/.test(t)) return;
                    if (t === 'post' || t === 'kirim' || t === 'balas' || t === 'reply' || t === 'send' ||
                        aria.includes('post') || aria.includes('kirim') || aria.includes('balas') ||
                        aria.includes('send') || aria.includes('reply')) {
                        cands.push(b);
                    }
                });
                if (!cands.length) return null;
                cands.sort((a, b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y);
                return cands[0];
            }
            let el = pick(document.querySelector('[role="dialog"]') || document.body);
            if (!el) {
                const all = [];
                document.querySelectorAll('button, [role="button"]').forEach(b => {
                    if (b.disabled) return;
                    const t = (b.textContent || '').trim().toLowerCase();
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    if (/like|repost|share|follow/.test(aria)) return;
                    if (/\d/.test(t)) return;
                    if (t === 'post' || t === 'kirim' || t === 'balas' || t === 'reply' || t === 'send' ||
                        aria.includes('post') || aria.includes('kirim') || aria.includes('balas') ||
                        aria.includes('send') || aria.includes('reply')) all.push(b);
                });
                if (!all.length) {
                    const dbg = [];
                    document.querySelectorAll('button, [role="button"]').forEach(b => {
                        const t=(b.textContent||'').trim(); const aria=b.getAttribute('aria-label')||'';
                        if (t || aria) dbg.push(t+'/'+aria+'/dis='+b.disabled);
                    });
                    return 'NO_BTN|' + JSON.stringify(dbg.slice(0,30));
                }
                all.sort((a, b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y);
                el = all[0];
            }
            el.click();
            return 'CLICKED:' + (el.textContent || '').trim();
        })()
    '''
    clicked = cdp_eval(send_expr, 15)
    if not clicked or clicked.startswith('NO_BTN'):
        time.sleep(3)
        clicked = cdp_eval(send_expr, 15)
    if not clicked or clicked.startswith('NO_BTN'):
        print("    Kirim button not found:", clicked)
        return False
    print("    Kirim clicked (JS):", clicked)
    time.sleep(5)
    # sukses = modal tertutup (dialog count 0) ATAU username muncul di halaman
    dlg = cdp_eval("""(()=>document.querySelectorAll('[role="dialog"]').length)()""", 10)
    cdp_navigate(url)
    time.sleep(4)
    verify_text = cdp_eval("document.body.innerText", 30)
    if (dlg == 0) or (YOUR_USERNAME and YOUR_USERNAME.lower() in verify_text.lower()):
        return True
    return False


def generate_alert(post_info, affiliate_link, success):
    fl = final_link(affiliate_link)
    print("\n" + "=" * 50)
    if success:
        print("THREADS POST SUCCESS!")
        print(f"  @{YOUR_USERNAME}")
        print(f"  {post_info['content'][:60]}...")
        print(f"  {fl}")
        print(f"  {post_info['category']}/{post_info.get('subcategory', '?')}")
        print(f"  {post_info['url']}")
    else:
        print("THREADS POST FAILED / skipped")
    print("=" * 50)


def run():
    print("THREADS AFFILIATE BOT v3 (Windows)")
    print("=" * 50)
    print(f"Account : @{YOUR_USERNAME}")
    print(f"Chrome  : {CHROME_HOST}:{CHROME_PORT}")
    print(f"DRY_RUN : {DRY_RUN}")
    print("=" * 50)
    post_links = scan_threads()
    if not post_links:
        print("No posts found (mungkin perlu login dulu di Chrome).")
        return
    print("\n[2/5] Analyzing posts...")
    target_post = None
    for link in post_links:
        print(f"  Checking: {link}")
        post_info = analyze_post(link)
        if post_info:
            target_post = post_info
            print(f"  Match: {post_info['category']}/{post_info.get('subcategory', '?')}")
            print(f"  Content: {post_info['content'][:60]}...")
            break
    if not target_post:
        print("\nNo matching skincare/makeup/parfum post found")
        return
    print("\n[3/5] Getting affiliate link...")
    affiliate_link = get_affiliate_link(target_post['category'], target_post.get('subcategory'))
    if not affiliate_link:
        print("No affiliate link untuk kategori ini (isi AFFILIATE_DB dulu).")
        return
    print(f"    Link: {final_link(affiliate_link)}")
    print("\n[4/5] Posting comment...")
    success = post_comment(target_post, affiliate_link)
    if success:
        save_posted(target_post['url'])
    print("\n[5/5] Result:")
    generate_alert(target_post, affiliate_link, success)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Pastikan Chrome berjalan di port %s dengan remote debugging." % CHROME_PORT)
