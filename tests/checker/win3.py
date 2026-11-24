import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
SEQS = [
 ["80 + 2 × 200", "480", "180/360×2π×40 + 2×40", "205.7", "480+205.7"],
 ["80 + 2 × 200", "480", "180/360×2π×40", "480 + 125.66", "605.7"],
 ["2 × 200", "80 + 400", "1/2 × π × 80", "480 + 125.66", "605.7"],
 ["1/2 × π × 80 + 80", "205.66 + 400", "605.7"],
 ["200 + 200", "400 + 80", "480 + π×40", "605.7"],
 ["π × 40 + 2 × 40", "205.66 + 2 × 200", "605.7"],
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 2000; k++) for (const q of window.__tt.take('m10D', 40)) if (q.dia && q.dia.type === 'window' && q.dia.w === 80 && q.dia.h === 200) return q; }")
        print(q["calc"], q["ans"])
        for seq in SEQS:
            prev = []; out = []
            for ln in seq:
                r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); out.append(f"{ln} → {r['kind']}{(' ('+r['msg'][:30]+')') if r.get('msg') else ''}")
                if r["kind"] == "step": prev.append(ln)
                if r["kind"] == "final": break
            print("  " + "  |  ".join(out))
        await b.close()
asyncio.run(main())
