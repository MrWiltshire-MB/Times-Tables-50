import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10D', 40)) if (q.dia && q.dia.type === 'window' && q.dia.w === 60 && q.dia.h === 200) return q; }")
        print(q["calc"], q["ans"])
        for ln, prev in [("200 + 200 + 60", []), ("l=180/360*2*pi*30", ["200 + 200 + 60"]), ("s = π × 60 / 2", []), ("l = 200", []), ("h = 200", []), ("l = π × 60", []),
                         ("π", ["60 + 2 × 200", "460"]), ("pi", []), ("2π", []), ("π/2", []), ("1/2 × π × 60", ["60 + 2 × 200", "460"]), ("460 + 94.25", ["60 + 2 × 200", "460"]), ("P = 2l + w + πr", []), ("P = 2h + w + l", [])]:
            r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:24} -> {r['kind']} {r.get('msg','')[:50]}")
        await b.close()
asyncio.run(main())
