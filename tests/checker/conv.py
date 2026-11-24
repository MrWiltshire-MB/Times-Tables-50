import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        for pat, t, lines in [("doorway", "m10A", ["0.9×100","90","30÷10","3","90+3"]), ("Chain costs", "m10A", ["150÷100","1.5","1.5×6"]),
                              ("rectangular prism", "m10K", None)]:
            q = await pg.evaluate("([pat, t]) => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take(t, 40)) if (q.html.includes(pat) && q.mwork) return q; }", [pat, t])
            if not q: print(pat, "none"); continue
            print(q["html"][:90], "|", q["calc"])
            import re
            n = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", q["html"])]
            if pat == "doorway": a, b2 = n[0], n[1]; lines = [f"{a}×100", f"{a*100:g}", f"{b2:g}÷10", f"{b2/10:g}", f"{a*100:g}+{b2/10:g}", f"{a}+{b2/1000:g}"]
            if pat == "Chain costs": pr, cm = n[0], n[1]; lines = [f"{cm:g}÷100", f"{cm/100:g}", f"{cm/100:g}×{pr:g}", f"{cm:g}×{pr:g}"]
            for ln in (lines or [q["calc"]]):
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); print(f"   {ln:12} -> {r['kind']}")
        await b.close()
asyncio.run(main())
