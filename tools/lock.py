"""Replace expired, unpaid demo sites with a 'demo ended' page.
Usage: python3 tools/lock.py [--paid slug1,slug2] [--now ISO]
Reads each site's expiry from the Date.parse("...") in its index.html."""
import sys, re, pathlib, datetime, html
root = pathlib.Path(__file__).resolve().parent.parent
args = sys.argv[1:]
paid = set(args[args.index("--paid") + 1].split(",")) if "--paid" in args else set()
now = datetime.datetime.fromisoformat(args[args.index("--now") + 1].replace("Z", "+00:00")) if "--now" in args else datetime.datetime.now(datetime.timezone.utc)
END = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>{name} | Demo ended</title>
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,sans-serif;background:#14110f;color:#f5efe8;text-align:center;padding:24px}}main{{max-width:34rem}}h1{{font-size:clamp(28px,6vw,44px);margin:0 0 12px}}p{{color:#cfc5ba;line-height:1.6}}a{{display:inline-block;margin-top:18px;padding:12px 22px;border-radius:999px;background:#f5b335;color:#14110f;font-weight:700;text-decoration:none}}</style></head>
<body><main><!-- demo-locked --><h1>This demo has ended</h1><p>The free demo website made for <b>{name}</b> was available until {label}. To put it live on your own domain for a one-time ${price}, just reply to our email or write to us.</p><a href="mailto:youssef.sameh@primeegy.com?subject={subj}">youssef.sameh@primeegy.com</a></main></body></html>"""
locked = []
for f in sorted(root.glob("*/index.html")):
    slug = f.parent.name
    t = f.read_text(encoding="utf-8")
    if "<!-- demo-locked -->" in t or slug in paid: continue
    m = re.search(r'Date\.parse\("([^"]+)"\)', t)
    if not m: continue
    exp = datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    if now < exp: continue
    name = html.unescape(re.search(r"<title>([^<|]+)", t).group(1).strip())
    label = (exp - datetime.timedelta(hours=5)).strftime("%B %-d")
    pm = re.search(r'<meta name="demo-price" content="(\d+)"', t)
    price = pm.group(1) if pm else "150"
    f.write_text(END.format(name=html.escape(name), label=label, price=price, subj=f"Website for {name}".replace(" ", "%20")), encoding="utf-8")
    locked.append(slug)
print("locked:", ",".join(locked) or "none")
