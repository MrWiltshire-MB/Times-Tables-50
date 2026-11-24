import asyncio, datetime, json
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
# (type, regex on html, function of numbers -> list of lines). Numbers taken from the generated question.
CASES = [
 ("m10B", r"paddock is (\d+) m long and (\d+) m wide\. Fencing costs \$(\d+)", lambda L,W,c: [f"{W}+{L}+{W}+{L}", f"{2*L+2*W}*{c}", f"{(2*L+2*W)*c}"], "intermediate perimeter"),
 ("m10B", r"paddock is (\d+) m long and (\d+) m wide\. Fencing costs \$(\d+)", lambda L,W,c: [f"{L}+{W}", f"{L+W}x2", f"{2*(L+W)} x {c} = {2*(L+W)*c}", f"${2*(L+W)*c}"], "half perimeter, x as times, $"),
 ("m10B", r"paddock is (\d+) m long and (\d+) m wide\. Fencing costs \$(\d+)", lambda L,W,c: [f"{L}+{W}+{L}", "1"], "3 sides only (should be WRONG)"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"{L}*2+2x={P}", f"2x={P-2*L}", f"x={(P-2*L)//2}"], "equation with x"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"2 × {L} + 2w = {P} cm", f"w = {(P-2*L)//2} cm"], "equation with w and units"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"2l + {2*L} = {P}", f"{(P-2*L)//2}"], "equation with l (a unit letter)"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"{L}*2", f"{P}-{2*L}", f"{P-2*L}/2", f"{(P-2*L)//2}"], "steps without equation"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"{L}", ], "just a question number (should be told, not marked)"),
 ("m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", lambda P,L: [f"x+x={P}"], "wrong equation (should be WRONG)"),
 ("m10C", r"circumference of ([\d.]+) (\w+)\.", None, "circle radius via 2π"),
 ("m10I", r"volume of (\d+) \w+³\. Its length is (\d+) \w+ and its width is (\d+)", lambda V,L,W: [f"{L}*{W}", f"{V}/{L*W}", f"{V//(L*W)}"], "prism height"),
 ("m10I", r"volume of (\d+) \w+³\. Its length is (\d+) \w+ and its width is (\d+)", lambda V,L,W: [f"{L}*{W}*h={V}", f"h={V//(L*W)}"], "prism height equation"),
 ("m10A", r"difference between (\d+) km and (\d+) m\.", lambda K,M: [f"{K} - {M/1000:g}", f"{K-M/1000:g} × 1000", f"{K*1000-M:g}"], "km then convert"),
 ("m10F", r"base of (\d+) m and a height of (\d+) m. Paint costs \$(\d+) per litre and 1 litre covers (\d+)", lambda B,H,c,cov: [f"{B}×{H}", f"{B*H}÷{cov}", f"{B*H//cov}×{c}", f"{B*H//cov*c}"], "paint cost"),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1200,"height":900}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,11,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        import re
        for t, rx, fn, label in CASES:
            q = await pg.evaluate("""([t, rx]) => { const r = new RegExp(rx); for (let k = 0; k < 400; k++) for (const q of window.__tt.take(t, 40)) { const h = q.html.replace(/<[^>]+>/g,''); if (q.mwork && r.test(h)) return q; } return null; }""", [t, rx])
            if not q: print("NO QUESTION", label); continue
            h = re.sub(r"<[^>]+>", "", q["html"]); m = re.search(rx, h)
            if fn is None:
                C = float(m.group(1)); import math
                lines = ([f"2×π", f"{C} ÷ (2×π)", f"{q['ans']}"] if "radius" in q["sub"] else [f"{C}÷π", f"{q['ans']}"])
            else:
                nums = [int(x) if x.isdigit() else float(x) for x in m.groups()]; lines = fn(*nums)
            await pg.evaluate("q => window.__tt.showQ(q)", q); await pg.wait_for_timeout(50)
            out = []
            for ln in lines:
                if not await pg.locator("#wInput").count(): out.append("(done)"); break
                await pg.fill("#wInput", ln); await pg.press("#wInput", "Enter"); await pg.wait_for_timeout(40)
                fb = (await pg.text_content("#feedback")).strip()[:40]
                out.append(f"{ln!r} -> {fb}")
            res = await pg.evaluate("() => window.__tt.qs && JSON.stringify(window.__tt.qs().length)")
            print(f"[{label}] {h[:70]} | ans {q['ans']} | sub: {q['sub'][:60]}")
            for o in out: print("     ", o)
        print("errors", errs); await b.close()
asyncio.run(main())
