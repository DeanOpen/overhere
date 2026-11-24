#!/usr/bin/env python3
"""Build the Over Here website (GitHub Pages) from the app's docs and App Store screenshots.

Usage: python3 site/build.py   → writes site/docs/
"""
import html, re, shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "docs"
EMAIL = "tech@nextwaves.com"

CSS = """
:root{--ink:#111016;--surface:#1C1B22;--raised:#2A2932;--spot:#FFD23F;--text:#fff;--muted:rgba(255,255,255,.62);--line:rgba(255,255,255,.09)}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ink);color:var(--text);font:17px/1.6 ui-rounded,"SF Pro Rounded",-apple-system,system-ui,"Segoe UI",Roboto,sans-serif}
a{color:var(--spot)}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px 0}
.brand{display:flex;align-items:center;gap:10px;color:var(--text);text-decoration:none;font-weight:900;font-size:20px}
.brand img{width:36px;height:36px;border-radius:9px}
nav{display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-weight:700;font-size:15px}
nav a{color:var(--muted);text-decoration:none}
nav a:hover,nav a.on{color:var(--text)}
.lang{background:var(--raised);border:0;color:var(--text);font:inherit;font-weight:800;border-radius:99px;padding:5px 12px;cursor:pointer}
html[lang=en] [data-l=vi],html[lang=vi] [data-l=en]{display:none!important}
.hero{text-align:center;padding:48px 0 24px}
.hero img.icon{width:112px;height:112px;border-radius:26px;box-shadow:0 12px 40px rgba(255,210,63,.25)}
h1{font-size:clamp(34px,7vw,60px);line-height:1.05;font-weight:900;margin:22px 0 12px;letter-spacing:-.02em}
.lead{color:var(--muted);font-size:clamp(17px,2.4vw,21px);max-width:640px;margin:0 auto}
.cta{display:inline-block;margin-top:26px;background:var(--spot);color:var(--ink);font-weight:900;text-decoration:none;padding:14px 26px;border-radius:99px}
.shots{display:flex;gap:14px;overflow-x:auto;padding:32px 0 8px;scroll-snap-type:x mandatory}
.shots img{height:min(560px,70vh);border-radius:22px;scroll-snap-align:center;flex:none}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;padding:32px 0}
.card{background:var(--surface);border-radius:22px;padding:22px}
.card h3{margin:0 0 6px;font-size:19px;font-weight:900}
.card p{margin:0;color:var(--muted);font-size:16px}
.doc{max-width:760px;padding:24px 0 48px}
.doc h1{font-size:clamp(30px,5vw,44px)}
.doc h2{font-size:22px;margin:34px 0 8px;font-weight:900}
.doc h3{font-size:18px;margin:24px 0 6px}
.doc p,.doc li{color:rgba(255,255,255,.86)}
.doc table{width:100%;border-collapse:collapse;font-size:15px;display:block;overflow-x:auto}
.doc th,.doc td{border-bottom:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}
.doc th{color:var(--muted);font-weight:800}
details{background:var(--surface);border-radius:16px;padding:14px 18px;margin:10px 0}
summary{font-weight:800;cursor:pointer}
details p,details ul{color:var(--muted);margin:10px 0 0}
.contact{background:var(--surface);border-radius:22px;padding:22px;margin-top:28px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:22px 0 40px;color:var(--muted);font-size:14px;display:flex;gap:16px;flex-wrap:wrap}
footer a{color:var(--muted)}
"""

JS = """
(function(){var d=document.documentElement,k='oh-lang',s=null;
try{s=localStorage.getItem(k)}catch(e){}
var l=s||((navigator.language||'').toLowerCase().indexOf('vi')===0?'vi':'en');
if(document.querySelector('[data-l]'))d.lang=l;
window.toggleLang=function(){d.lang=d.lang==='vi'?'en':'vi';try{localStorage.setItem(k,d.lang)}catch(e){}};})();
"""


def page(name, title, body, bilingual=True, desc="Find your friends in a crowd, with exact distance and direction."):
    nav = [("index.html", "Over Here", "Over Here"), ("support.html", "Support", "Hỗ trợ"),
           ("privacy.html", "Privacy", "Quyền riêng tư"), ("terms.html", "Terms", "Điều khoản")]
    links = "".join(
        f'<a href="{h}"{" class=on" if h == name else ""}><span data-l="en">{en}</span><span data-l="vi">{vi}</span></a>'
        if bilingual else f'<a href="{h}"{" class=on" if h == name else ""}>{en}</a>'
        for h, en, vi in nav[1:])
    toggle = '<button class="lang" onclick="toggleLang()" aria-label="Language"><span data-l="en">Tiếng Việt</span><span data-l="vi">English</span></button>' if bilingual else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="icon.png"><link rel="apple-touch-icon" href="icon.png">
<style>{CSS}</style><script>{JS}</script></head>
<body><div class="wrap">
<header><a class="brand" href="index.html"><img src="icon.png" alt="">Over Here</a><nav>{links}{toggle}</nav></header>
{body}
<footer><span>© 2026 Over Here</span><a href="support.html">Support</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Use</a><a href="mailto:{EMAIL}">{EMAIL}</a></footer>
</div></body></html>
"""


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\b([\w.+-]+@[\w-]+\.[\w.]+)\b", r'<a href="mailto:\1">\1</a>', s)
    return s


def md(text):
    """Enough Markdown for the app's docs: headings, paragraphs, lists, tables, bold/italic."""
    out, para, lst, table = [], [], [], []

    def flush():
        nonlocal para, lst, table
        if para: out.append(f"<p>{inline(' '.join(para))}</p>"); para = []
        if lst: out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>"); lst = []
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table if not re.match(r"^\|[\s:|-]+\|$", r.strip())]
            h = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"); table = []

    for line in text.splitlines():
        if m := re.match(r"^(#{1,3}) (.*)", line):
            flush(); n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif line.startswith("|"):
            if para or lst: flush()
            table.append(line)
        elif m := re.match(r"^\s*[-*] (.*)", line):
            if para or table: flush()
            lst.append(m.group(1))
        elif not line.strip():
            flush()
        else:
            if lst or table: flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


def L(en, vi):
    return f'<span data-l="en">{en}</span><span data-l="vi">{vi}</span>'


FEATURES = [
    ("Exact distance and direction", "Khoảng cách và hướng chính xác",
     "A live arrow points straight at your friend (iPhone 11 or later).", "Mũi tên chỉ thẳng tới bạn mình (iPhone 11 trở lên)."),
    ("Ping and beacon", "Ping và đèn hiệu",
     "Let a friend know you're looking for them, or light up your screen so they spot you.", "Báo cho bạn biết mình đang tìm, hoặc bật màn hình sáng cho bạn dễ thấy."),
    ("Chat with no signal", "Mất sóng vẫn nhắn được",
     "Group and private messages go phone to phone, end-to-end encrypted.", "Chat nhóm và nhắn riêng đi thẳng từ máy sang máy, mã hoá đầu cuối."),
    ("Meet up", "Hẹn gặp",
     "Set a place and time. Everyone sees a countdown and gets a reminder.", "Chọn chỗ và giờ. Cả nhóm thấy đếm ngược và được nhắc trước."),
    ("Private groups", "Nhóm riêng",
     "Invite people standing next to you, or share a QR code. Only invited people can join.", "Mời người đứng cạnh, hoặc chia sẻ mã QR. Chỉ người được mời mới vào được."),
    ("No account, no tracking", "Không tài khoản, không theo dõi",
     "No servers, no ads, no analytics. Your data stays on your group's phones.", "Không máy chủ, không quảng cáo, không thu thập dữ liệu. Dữ liệu chỉ nằm trên máy của nhóm."),
]

FAQ = [
    ("Do my friends need the app too?", "Bạn bè có cần cài app không?",
     "Yes. Everyone you want to find needs Over Here on their iPhone and has to be in the same group.",
     "Có. Mọi người muốn tìm nhau đều cần cài Over Here và ở chung một nhóm."),
    ("Why don't I see the arrow?", "Sao mình không thấy mũi tên?",
     "The arrow needs Ultra Wideband on both phones (iPhone 11 or later, not iPhone SE) and works best up close, in open space. Further away you still see the distance via Bluetooth. Check that Nearby Interaction is allowed in Settings → Over Here.",
     "Mũi tên cần chip Ultra Wideband ở cả hai máy (iPhone 11 trở lên, không phải iPhone SE) và chính xác nhất khi ở gần, chỗ thoáng. Ở xa hơn bạn vẫn thấy khoảng cách qua Bluetooth. Kiểm tra quyền Tương tác lân cận trong Cài đặt → Over Here."),
    ("How do I add someone to my group?", "Làm sao thêm người vào nhóm?",
     "Stand within about 3 m of them, tap + then Invite, and check that both phones show the same safety code. Or let them scan your group's QR code.",
     "Đứng cách nhau khoảng 3 m, bấm + rồi Mời, và kiểm tra hai máy hiện cùng một mã an toàn. Hoặc cho họ quét mã QR của nhóm."),
    ("Does it need internet?", "Có cần internet không?",
     "No. Finding, pings and chat work over Bluetooth and Ultra Wideband between phones. Only the optional map uses the internet to load map images.",
     "Không. Tìm nhau, ping và nhắn tin chạy qua Bluetooth và Ultra Wideband giữa các máy. Chỉ bản đồ (tuỳ chọn) cần mạng để tải hình bản đồ."),
    ("Pings or messages arrive late", "Ping hoặc tin nhắn đến chậm",
     "Keep Bluetooth on and allow notifications for Over Here. Don't force-quit the app from the app switcher, so it can keep receiving in the background.",
     "Để Bluetooth bật và cho phép thông báo của Over Here. Đừng vuốt tắt app trong trình đa nhiệm, để app còn nhận được khi chạy nền."),
    ("Can I try it without a second phone?", "Thử được khi chỉ có một máy không?",
     "Yes. Turn on demo friends (on the intro, or Profile → More → Demo friends) to try every feature on your own.",
     "Được. Bật bạn bè demo (ở màn hình giới thiệu, hoặc Hồ sơ → Thêm → Bạn bè demo) để tự thử mọi tính năng."),
    ("How do I delete my data?", "Làm sao xoá dữ liệu?",
     "Everything is stored on your phone. Leaving a group clears its chat, and deleting the app removes the rest. We have no copy on any server.",
     "Mọi thứ đều nằm trên máy bạn. Rời nhóm sẽ xoá chat của nhóm đó, xoá app sẽ xoá phần còn lại. Chúng tôi không lưu bản nào trên máy chủ."),
]


def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    Image.open(ROOT / "App/Assets.xcassets/AppIcon.appiconset/icon.png").convert("RGB").resize((256, 256), Image.LANCZOS).save(OUT / "icon.png")
    shots = {}
    for lang in ("en", "vi"):
        shots[lang] = []
        for f in sorted((ROOT / "screenshots/appstore" / lang / "iphone-6.3").glob("*.png"))[:6]:
            im = Image.open(f).convert("RGB"); im = im.resize((560, round(im.height * 560 / im.width)), Image.LANCZOS)
            name = f"img/{lang}-{f.stem}.jpg"; im.save(OUT / name, quality=84, optimize=True)
            shots[lang].append(name)

    gallery = "".join(f'<div class="shots" data-l="{l}">' + "".join(f'<img src="{s}" alt="" loading="lazy">' for s in shots[l]) + "</div>" for l in ("en", "vi"))
    cards = "".join(f'<div class="card"><h3>{L(a, b)}</h3><p>{L(c, d)}</p></div>' for a, b, c, d in FEATURES)
    index = f"""<section class="hero"><img class="icon" src="icon.png" alt="Over Here">
<h1>{L("Lost each other?<br>Over Here.", "Lạc nhau?<br>Over Here.")}</h1>
<p class="lead">{L("Find your friends at concerts, festivals, airports and theme parks. Exact distance and direction, no internet, no account.",
                   "Tìm bạn bè ở concert, lễ hội, sân bay, công viên giải trí. Khoảng cách và hướng chính xác, không cần mạng, không cần tài khoản.")}</p>
<a class="cta" href="support.html">{L("Get help", "Cần hỗ trợ")}</a></section>
{gallery}<section class="grid">{cards}</section>"""
    (OUT / "index.html").write_text(page("index.html", "Over Here: Find Friends Nearby", index))

    faq = "".join(f"<details><summary>{L(a, b)}</summary><p>{L(c, d)}</p></details>" for a, b, c, d in FAQ)
    support = f"""<section class="doc"><h1>{L("Support", "Hỗ trợ")}</h1>
<p>{L("Answers to common questions. Can't find yours? Email us and we'll get back to you.", "Giải đáp các câu hỏi thường gặp. Chưa thấy câu trả lời? Gửi email cho chúng tôi.")}</p>
{faq}
<div class="contact"><h2 style="margin-top:0">{L("Contact", "Liên hệ")}</h2>
<p>{L("Email", "Email")}: <a href="mailto:{EMAIL}?subject=Over%20Here%20support">{EMAIL}</a></p>
<p style="color:var(--muted)">{L("Please include your iPhone model and iOS version. The Diagnostics button on the Your group screen shows details that help us.",
                                   "Vui lòng ghi kèm đời iPhone và phiên bản iOS. Nút Chẩn đoán trong màn hình Nhóm của bạn có thông tin giúp chúng tôi xử lý nhanh hơn.")}</p></div>
</section>"""
    (OUT / "support.html").write_text(page("support.html", "Over Here Support", support))

    for name, src, title in (("privacy.html", "docs/PRIVACY.md", "Over Here Privacy Policy"), ("terms.html", "docs/TERMS.md", "Over Here Terms of Use")):
        body = f'<section class="doc">{md((ROOT / src).read_text())}</section>'
        (OUT / name).write_text(page(name, title, body, bilingual=False))
    (OUT / ".nojekyll").write_text("")
    print("built", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    build()
