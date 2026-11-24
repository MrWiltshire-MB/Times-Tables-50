import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 3000; k++) for (const q of window.__tt.take('m10B', 40)) if (q.html === 'A rectangle has a perimeter of 30 cm and a length of 8 cm.' && q.mwork) return q; }")
        print(q["calc"], q["ans"])
        for ln, prev in [("2*8",[]),("2×8",[]),("30-16",["2*8"]),("30-2*8",[]),("(30-16)/2",[]),("14/2",["30-16"]),("14÷2",["30-2*8"]),("30/2",[]),("15-8",["30/2"]),("30÷2-8",[]),("30-8-8",[]),("14÷2",["30-8-8"]),("7",["14/2"]),("w=7",["14/2"]),("w = (30-16)/2",[]),
                         ("30-8",[]),("22/2",["30-8"]),("30/4",[])]:
            r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:16} after {prev!s:18} -> {r['kind']} {r.get('msg','')}")
        await b.close()
asyncio.run(main())
