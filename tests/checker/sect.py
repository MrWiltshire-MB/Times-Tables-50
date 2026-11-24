import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        for want in ["sector", "quad", "semi"]:
            q = await pg.evaluate("""(w) => { for (let k = 0; k < 800; k++) for (const q of window.__tt.take('m10D', 40)) { const d = q.dia || {};
               if (w === 'sector' && d.type === 'sector' && !d.arcOnly && d.a !== 90) return q; if (w === 'quad' && d.type === 'sector' && d.a === 90) return q; if (w === 'semi' && d.type === 'semi') return q; } }""", want)
            d = q["dia"]; a = d.get("a", 180); r = d.get("r", d.get("d", 0) / 2)
            print(f"== {want} {d} ans {q['ans']} calc {q['calc']}")
            for ln in [f"{a}/360*2pi*r+2r", f"P = {a}/360*2pi*r+2r", f"{a}/360*2pi*{r:g}+2*{r:g}", f"{a}/360*2*pi*{r:g}+2*{r:g}", f"θ/360×2πr+2r", "2πr×θ/360 + 2r", f"{a}/360*2pi*r+r", f"{a}/360*2pi*{r:g}+{r:g}", "πd/2 + d", "πr + 2r", f"pi*{r:g}+2*{r:g}"]:
                j = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print(f"   {ln:28} -> {j['kind']} {j.get('msg','')[:45]}")
        await b.close()
asyncio.run(main())
