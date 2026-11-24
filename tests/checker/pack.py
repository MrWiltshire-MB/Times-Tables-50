import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        q = await pg.evaluate("() => { for (let k = 0; k < 3000; k++) for (const q of window.__tt.take('m10I', 40)) if (/A box 30 cm long, 25 cm high and 12 cm wide is packed with small boxes 10 cm long, 5 cm high and 2 cm wide/.test(q.html)) return q; }")
        print(q["calc"], q["ans"], q.get("model"), q.get("alt"))
        for ln, prev in [("a=30*25*12",[]),("30*25*12",[]),("V=30*25*12",[]),("v=30×25×12",[]),("9000",[]),("10*5*2",[]),("10*5*2",["30*25*12"]),("v=10×5×2",["30*25*12"]),("9000/100",["30*25*12","10*5*2"]),("9000÷100",["30*25*12","10*5*2"]),("90",["30*25*12","10*5*2","9000/100"]),
                         ("30*25*12/(10*5*2)",[]),("(30*25*12)÷(10*5*2)",[]),("30/10",[]),("25/5",[]),("12/2",[]),("3*5*6",["30/10","25/5","12/2"]),("30/10*25/5*12/2",[]),("90",["3*5*6"]),
                         ("30*25",[]),("30*25*12/10",[]),("9000/50",["30*25*12"]),("30*25*12*10*5*2",[])]:
            r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:22} after {prev!s:40} -> {r['kind']} {r.get('msg','')}")
        await b.close()
asyncio.run(main())
