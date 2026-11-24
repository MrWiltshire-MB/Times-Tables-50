import asyncio, re
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
F="final"; ST="step"; W="wrong"; SAY="say"
CASES = {
 "window": [("{p}+180/360*2*pi*{r}", W), ("{base}+180/360*2*pi*{r}", ST), ("{w} + 2×{h} + 1/2×π×{w}", ST), ("{w}+{h}+{h}+π×{w}/2", ST), ("2×{h}+{w}", ST), ("π×{w}/2", ST), ("1/2×π×{w}", ST), ("π×{r}", ST),
   ("P = 2h + w + ½πw", ST), ("P = 2h + w + πr", ST), ("p=2l+b+πd/2", ST), ("P = 2h + w + πw", W), ("P = 2h + 2w + πr", W), ("P = 2×{h} + {w} + π×{r}", ST), ("P = 2h + w + πr = {ans}", ST),
   ("r = {r}", ST), ("r = {w}/2", ST), ("d = {w}", SAY), ("{ans}", F), ("P = {ans}", F), ("{p}", W)],
 "arc": [("p={a}/360*2pi*r", ST), ("p = θ/360 × 2πr", ST), ("a = {a}/360 × 2πr", ST), ("p = {a}/360×2πr + 2r", W), ("l = θ/360 × 2πr", ST), ("l = θ/360 × 2π{rr}", ST), ("{a}/360 × 2 × π × {rr}", ST), ("l = {a}/360 × 2πr", ST), ("l = θ/360 × πr", W), ("2πr", W), ("2×π×{rr}", ST), ("{ans}", F)],
 "sector": [("P = θ/360 × 2πr + 2r", ST), ("p = {a}/360×2πr + 2r", ST), ("{a}/360×2×π×{rr} + 2×{rr}", ST), ("P = θ/360 × 2πr + r", W), ("2×{rr}", ST), ("{ans}", F)],
 "semi": [("P = d + ½πd", ST), ("P = d + πr", ST), ("P = d + πd", W), ("{dd} + π×{dd}/2", ST), ("π×{dd}/2", ST), ("{ans}", F)],
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        bad=tot=0
        for name, lines in CASES.items():
            q = await pg.evaluate("""(name) => { for (let k = 0; k < 800; k++) for (const q of window.__tt.take('m10D', 40)) { const d = q.dia || {};
                if (name === 'window' && d.type === 'window') return q; if (name === 'semi' && d.type === 'semi') return q;
                if (name === 'arc' && d.type === 'sector' && d.arcOnly) return q; if (name === 'sector' && d.type === 'sector' && !d.arcOnly && d.a !== 90) return q; } return null; }""", name)
            d = q["dia"]
            sub = {"{ans}": "%g" % q["ans"]}
            if name == "window": sub.update({"{w}": str(d["w"]), "{h}": str(d["h"]), "{r}": "%g" % (d["w"]/2), "{p}": str(2*d["w"]+2*d["h"]), "{base}": str(d["w"]+2*d["h"])})
            if name in ("arc","sector"): sub.update({"{a}": str(d["a"]), "{rr}": "%g" % d["r"]})
            if name == "semi": sub.update({"{dd}": "%g" % d["d"]})
            print(f"== {name}: {re.sub('<[^>]+>','',q['html'])} {d} ans {q['ans']}")
            for ln, exp in lines:
                for k, v in sub.items(): ln = ln.replace(k, v)
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, ln]); tot += 1; ok = r["kind"] == exp; bad += not ok
                print(f"   {'ok  ' if ok else 'FAIL'} {ln!r:36} -> {r['kind']}{'' if ok else '  (expected '+exp+') '+r.get('msg','')[:40]}")
        print(f"{tot-bad}/{tot}; errors {errs}"); await b.close()
asyncio.run(main())
