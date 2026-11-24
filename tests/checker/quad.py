import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10D', 40)) if (q.dia && q.dia.type === 'sector' && q.dia.a === 90 && q.dia.r === 5) return q; }")
        print(q["calc"], q["ans"])
        for ln in ["90/360×π×5", "1/4×π×5", "π×5", "90/360×2×π×5", "1/4×2π×5", "2×π×5", "2π×5/4", "90/360×2π×5 + 2×5", "2×5", "10 + 7.85", "π×5/2"]:
            r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print(f"   {ln:22} -> {r['kind']}")
        await b.close()
asyncio.run(main())
