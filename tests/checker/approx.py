import asyncio, json
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
CASES = {
 "22/7": ("d", 28, [("c=π×d",[]), ("c=22/7*28",["c=π×d"]), ("c=22/7*28",[]), ("22/7*28",[]), ("C = 22/7 × 28",[]), ("28/7*22",[]), ("28÷7",[]), ("4×22",["28÷7"]), ("c=4×22",["28÷7"]), ("c = 88",["22/7*28"]), ("88",["22/7*28"]), ("88 m",["22/7*28"]),
          ("c=π×28",[]), ("c=2×22/7×28",[]), ("c=22/7*14",[]), ("c=3.14*28",[]), ("c=22/7*28=88",[])]),
 "3.14": ("r", 5, [("c=2πr",[]), ("c=2×3.14×5",[]), ("2*3.14*5",[]), ("c = 3.14 × 10",[]), ("3.14×10",[]), ("2×5",[]), ("c=31.4",["2*3.14*5"]), ("31.4",["2*3.14*5"]),
          ("c=3.14×5",[]), ("c=2×π×5",[]), ("c=22/7×10",[])]),
 "3.": ("d", 12, [("c=π×d",[]), ("c=3×12",[]), ("3*12",[]), ("c=36",["3*12"]), ("36",["3*12"]), ("c=π×12",[]), ("c=3×6",[])]),
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        for key, (mode, v, lines) in CASES.items():
            q = await pg.evaluate("([key, mode, v]) => { for (let k = 0; k < 3000; k++) for (const q of window.__tt.take('m10C', 40)) if (q.html.includes('Use π ≈ ' + (key === '22/7' ? '<span class=\"frac\">' : key)) && q.dia && q.dia.mode === mode && q.dia.v === v && q.mwork) return q; }", [key, mode, v])
            if not q: print(key, "no question (maybe not a working question)"); continue
            print(f"[{key}] {q.get('calc')} = {q['ans']}")
            for ln, prev in lines:
                r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev]); print(f"   {ln:22} after {prev!s:22} -> {r['kind']} {r.get('msg','')}")
        await b.close()
asyncio.run(main())
