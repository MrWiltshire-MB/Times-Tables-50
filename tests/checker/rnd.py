import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10D', 40)) if (q.dia && q.dia.type === 'sector' && q.dia.a === 90 && q.dia.r === 5) return q; }")
        print(q["calc"], q["ans"], q["sub"])
        prev=["90/360×2×π×5 + 2×5"]
        for ln in ["17.85","17.9","17.8","18","P = 17.85","P = 17.9","p=17.9cm","17.9 cm","17.85 cm","7.85+10 = 17.85","7.85+10 = 17.9","17.90","17.854"]:
            r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:22} -> {r['kind']} {r.get('msg','')}")
        # 2dp question
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10C', 40)) if (/2 decimal/.test(q.sub) && q.dia) return q; }")
        print(q["calc"], q["ans"], q["sub"])
        a=q["ans"]
        for ln in [f"{a:.2f}", f"{a:.3f}", f"{a+0.01:.2f}", f"{a:.1f}", q["calc"]+f" = {a:.2f}", q["calc"]+f" = {a:.4f}"]:
            r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print(f"   {ln:30} -> {r['kind']} {r.get('msg','')}")
        await b.close()
asyncio.run(main())
