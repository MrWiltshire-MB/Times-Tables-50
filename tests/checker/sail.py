import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 3000; k++) for (const q of window.__tt.take('m10G', 40)) if (/One has base 2 m and height 8 m. The other has base 4 m and height 16 m. Sail material costs \\$150/.test(q.html)) return q; }")
        print(q and q["calc"], q and q["ans"])
        P = ["1/2*2*8=8","1/2*4*16=32","32+8=40"]
        for ln, prev in [("40×100=4,000",P),("40×100",P),("4,000",P),("40*150",P),("6000",P+["40*150"]),("40×150=6000",P),("4*1000",[]),("8×100",[])]:
            r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:14} -> {r['kind']} {r.get('msg','')}")
        await b.close()
asyncio.run(main())
