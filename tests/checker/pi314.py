import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 3000; k++) for (const q of window.__tt.take('m10D', 40)) if (q.mwork && Math.abs(q.ans - 3.14) < 0.001) return q; }")
        print(q and (q["html"], q["calc"], q["ans"]))
        if q:
            for ln in ["3.14", "l = 3.14", "3.14 cm", "2*3.14*1", "180/360*2*pi*1"]:
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print("  ", ln, "->", r["kind"], r.get("msg","")[:40])
        q = await pg.evaluate("() => { for (let k = 0; k < 800; k++) for (const q of window.__tt.take('m10D', 40)) if (q.dia && q.dia.type === 'semi') return q; }")
        d = q["dia"]["d"]
        for ln in [f"l = π×{d:g}/2", f"l = 180/360×2π×{d/2:g}", "P = d + l", f"l = π×{d:g}"]:
            r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print("  semi", ln, "->", r["kind"])
        await b.close()
asyncio.run(main())
