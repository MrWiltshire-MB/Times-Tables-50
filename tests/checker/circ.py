import asyncio, re
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
F="final"; ST="step"; W="wrong"; SAY="say"
CASES = {
 "r": [("c = π×{v}", W, []), ("c = πx{v}", W, []), ("c = 2π×{v}", ST, []), ("c = 2πr", ST, []), ("c=2pi*{v}", ST, ["c = 2πr"]), ("π×{v}", W, []), ("d = 2×{v}", ST, []), ("c = π × {d}", ST, ["d = 2×{v}"]),
       ("d = {v}", W, []), ("{ans}", F, []), ("c = {ans}", F, []), ("c = {half}", W, [])],
 "d": [("c = 2π×r", ST, []), ("c=2pi*{h}", ST, ["c = 2π×r"]), ("c = 2π × {h}", ST, []), ("r = {h}", ST, []), ("r = {v}", W, []), ("c = π×{v}", ST, []), ("c = 2π×{v}", W, []), ("c = π×{h}", W, []), ("{ans}", F, [])],
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        bad=tot=0
        for mode, lines in CASES.items():
            q = await pg.evaluate("""(mode) => { for (let k = 0; k < 800; k++) for (const q of window.__tt.take('m10C', 40)) { const d = q.dia || {}; if (q.mwork && d.type === 'circle' && d.mode === mode && !/3.14|22/.test(q.sub + q.html)) return q; } return null; }""", mode)
            v = q["dia"]["v"]; sub = {"{v}": "%g" % v, "{ans}": "%g" % q["ans"], "{d}": "%g" % (2*v), "{h}": "%g" % (v/2), "{half}": "%.2f" % (q["ans"]/2)}
            print(f"== {mode}={v}: ans {q['ans']} ({q['calc']})")
            for ln, exp, prev in lines:
                f = lambda x: [x := x.replace(k, val) for k, val in sub.items()][-1]
                ln2 = f(ln); prev2 = [f(x) for x in prev]
                r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln2, prev2]); tot += 1; ok = r["kind"] == exp; bad += not ok
                print(f"   {'ok  ' if ok else 'FAIL'} {ln2!r:24} {('after '+str(prev2)) if prev2 else '':28} -> {r['kind']}{'' if ok else '  (expected '+exp+') '+r.get('msg','')[:40]}")
        print(f"{tot-bad}/{tot}; errors {errs}"); await b.close()
asyncio.run(main())
