import asyncio, json
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        for k in range(3):
            q = await pg.evaluate("() => { for (let k = 0; k < 800; k++) for (const q of window.__tt.take('m10B', 40)) if (/right angles/.test(q.html) && q.mwork) return q; }")
            print(json.dumps(q["dia"]), "|", q["calc"], "=", q["ans"])
            d = q["dia"]; nums = [v for v in d.values() if isinstance(v, (int, float))]
            print("  dia numbers:", nums)
            lines = [str(q["ans"]), "1+1+" + str(q["ans"]-2), "2×%s" % q["ans"], q["calc"]]
            for ln in lines:
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print("   ", ln, "->", r["kind"], r.get("msg","")[:40])
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10B', 40)) if (/right angles/.test(q.html) && q.mwork && q.dia.W === 10 && q.dia.H === 11 && q.dia.a === 7 && q.dia.b === 6) return q; }"); print("PHOTO Q", q and q["calc"], q and q["dia"], q and q["ans"], q and q["html"])
        if q:
            for ln in ["11+7+5+3+6+10", "11+7+5+3+6+10 = 42", "11-6", "10-7", "11+7+4+3+6+11", "42"]:
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print("  photo:", ln, "->", r["kind"], r.get("msg","")[:40])
        await b.close()
asyncio.run(main())
