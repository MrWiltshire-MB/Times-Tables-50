import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        old = {"t":"m10I","size":"text","kb":"decimal","html":"A box 36 cm long, 15 cm high and 10 cm wide is packed with small boxes 6 cm long, 3 cm high and 2 cm wide.","sub":"How many small boxes fit? Write the calculation, then the answer.","ans":150,"hint":"x","calc":"6 × 5 × 5","fact":"6 × 5 × 5 = <b>150</b> boxes","kind":"work","mwork":True,"min":2,"model":["6 × 5 × 5","150"]}
        for ln, prev in [("6*3*2",[]),("V=36×15×10",[]),("v=6×3×2",["V=36×15×10"]),("5400/36",["36*15*10","6*3*2"]),("36/6",[]),("6*5*5",[]),("150",["5400/36"])]:
            r = await pg.evaluate("([q, l, p]) => { q = JSON.parse(JSON.stringify(q)); const r = window.__tt.judgeLine(l, q, p); r.model = q.model[0]; return r; }", [old, ln, prev]); print(f"   {ln:14} after {prev!s:28} -> {r['kind']} {r.get('msg','')} | model now: {r['model']}")
        oldw = {"t":"m10B","html":"A rectangle has a perimeter of 30 cm and a length of 8 cm.","sub":"Find its width. Write the calculation, then the answer.","ans":7,"suf":"cm","calc":"(30 − 16) ÷ 2","kind":"work","mwork":True,"min":2,"model":["(30 − 16) ÷ 2","7 cm"]}
        r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [oldw, "30/2"]); print("old width q, 30/2 ->", r)
        await b.close()
asyncio.run(main())
