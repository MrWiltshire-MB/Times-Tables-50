import asyncio, datetime, json, re
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
# Each case: type, regex, then list of (line, expected kind, optional previous lines). {a},{b}.. are regex groups; {ans} the answer.
F="final"; ST="step"; W="wrong"; SAY="say"
CASES = [
 ("circle diameter", "m10C", r"circumference of ([\d.]+) (\w+)\.", "diameter", [
   ("{a}/pi=d", ST), ("{a}/pi = d", ST), ("d={a}/pi", ST), ("d = {a} ÷ π", ST), ("{a} ÷ π", ST), ("{a}/3.14", SAY), ("C = πd", ST), ("c=pi*d", ST), ("d = c/π", ST), ("d=c÷pi", ST),
   ("C = 2πr", ST), ("d = 2r", ST), ("C = πr", W), ("d = c × π", W), ("{a} = πd", ST), ("{a} = π × d", ST), ("πd = {a}", ST), ("{a} = 2πd", W), ("d × π = {a}", ST),
   ("{a} = 2πr", ST), ("{a} = 2 × pi × r", ST), ("{a} = πr", W), ("C = πd = {a}", ST),
   ("{ans}", F), ("d = {ans}", F), ("{ans} = d", F), ("d={ans}mm", F), ("= {ans}", F), ("≈ {ans}", F), ("{a}/pi = {ans}", F), ("d = {a}/π = {ans}", F), ("{a}/pi ≈ {ans}", F),
   ("C = π × {ans}", ST), ("C = {a}", SAY), ("{a} = C", SAY), ("{a}", SAY), ("d = d", W), ("{ans}+0", SAY), ("1+1", W), ("{a}×π", W), ("{a}/pi/2", W), ("hello", SAY), ("diameter = {ans}", F),
 ]),
 ("circle radius", "m10C", r"circumference of ([\d.]+) (\w+)\.", "radius", [
   ("c = π × d", ST), ("{a}=pi*d", ST), ("{a} = π × d", ST), ("d = {a}/π", ST), ("{a} = 2 × π × r", ST), ("{a}=2*pi*d", W), ("C = πd = {a}", ST), ("c = 2πr = {a}", ST), ("C = πr = {a}", W), ("d = 2r", ST), ("{a} = πd = 2πr", ST),
   ("{a}/pi/2", ST), ("{a} ÷ (2 × π)", ST), ("r = {a}/(2pi)", ST), ("2 × π", ST), ("{a}/pi", ST), ("C = 2πr", ST), ("r = C/(2π)", ST), ("r = d/2", ST), ("{a} = 2πr", ST), ("2πr = {a}", ST), ("{a} = πr", W), ("r = {ans}", F), ("{a}/pi/2 = {ans}", F),
 ]),
 ("rect width", "m10B", r"perimeter of (\d+) cm and a length of (\d+) cm", None, [
   ("P = 2l + 2w = {a}", ST), ("{a} = 2l + 2w", ST), ("{a} = l + w", W), ("{a} = 2×{b} + 2l", ST),
   ("P = 2l + 2w", ST), ("p=2(l+w)", ST), ("P = l + w", W), ("{b}*2+2x={a}", ST), ("2×{b} + 2w = {a}", ST), ("{a} = 2({b} + w)", ST), ("{a} - 2×{b}", ST), ("{b}+{b}", ST), ("({a} - 2×{b}) ÷ 2", ST),
   ("w = ({a} - 2×{b}) ÷ 2 = {ans}", F), ("w = {ans}", F), ("{ans} cm", F), ("l = {b}", SAY), ("x + x = {a}", W), ("x = x", W), ("{a}/2", ST), ("{a}/2 - {b}", ST), ("{a}-{b}", W),
 ]),
 ("paddock cost", "m10B", r"paddock is (\d+) m long and (\d+) m wide\. Fencing costs \$(\d+)", None, [
   ("{b}+{a}+{b}+{a}", ST), ("{a}+{b}", ST), ("2×{a}", ST), ("2×{a}+2×{b}", ST), ("P = 2l+2w", ST), ("{a}+{b}+{a}", W), ("{a}×{c}", W), ("{a}×{b}", W), ("{ans}", F), ("${ans}", F), ("(2×{a}+2×{b})×{c} = {ans}", F), ("{c}", SAY),
 ]),
 ("tri area", "m10G", r"^A triangle$", None, [
   ("A = 1/2 b h", ST), ("a=½bh", ST), ("A = bh/2", ST), ("A = b × h ÷ 2", ST), ("A = bh", W), ("A = 1/2 × b + h", W),
 ]),
 ("prism height", "m10I", r"volume of (\d+) \w+³\. Its length is (\d+) \w+ and its width is (\d+)", None, [
   ("V = l × w × h = {a}", ST), ("{a} = lwh", ST), ("{a} = l + w + h", W),
   ("V = lwh", ST), ("v = l × w × h", ST), ("V = l + w + h", W), ("{a} = {b} × {c} × h", ST), ("{b}*{c}*h={a}", ST), ("h = {a} ÷ ({b} × {c})", ST), ("{b}×{c}", ST), ("{a}÷{b}", ST), ("{a}÷{b}÷{c}", ST), ("h={ans}", F), ("{a}×{b}", W), ("{a}-{b}", W),
 ]),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        bad = 0; total = 0
        for label, t, rx, subrx, lines in CASES:
            q = await pg.evaluate("""([t, rx, subrx]) => { const r = new RegExp(rx), s = subrx && new RegExp(subrx); for (let k = 0; k < 600; k++) for (const q of window.__tt.take(t, 40)) { const h = q.html.replace(/<[^>]+>/g,''); if (q.mwork && r.test(h) && (!s || s.test(q.sub))) return q; } return null; }""", [t, rx, subrx])
            if not q: print("NO QUESTION", label); continue
            h = re.sub(r"<[^>]+>", "", q["html"]); m = re.search(rx, h); g = m.groups()
            fmt = lambda x: x.replace("{ans}", ("%g" % q["ans"])).replace("{a}", g[0] if len(g)>0 else "").replace("{b}", g[1] if len(g)>1 else "").replace("{c}", g[2] if len(g)>2 else "")
            print(f"== {label}: {h[:60]} | calc {q['calc']} = {q['ans']}")
            for ln, exp in lines:
                line = fmt(ln)
                r = await pg.evaluate("([q, l]) => window.__tt.judgeLine(l, q, [])", [q, line])
                total += 1; ok = r["kind"] == exp
                if not ok: bad += 1
                print(f"   {'ok  ' if ok else 'FAIL'} {line!r:38} -> {r['kind']}{'' if ok else '  (expected ' + exp + ')'}{'  [' + r.get('msg','')[:40] + ']' if r['kind']=='say' and not ok else ''}")
        # endless-line guards
        q = await pg.evaluate("""() => { for (let k = 0; k < 600; k++) for (const q of window.__tt.take('m10B', 40)) if (/paddock/.test(q.html)) return q; }""")
        L, Wd, c = map(int, re.search(r"is (\d+) m long and (\d+) m wide\. Fencing costs \$(\d+)", q["html"]).groups()); P = 2*L+2*Wd
        chain = [f"{L}+{Wd}", f"{L+Wd}×2", f"{P}", f"2×{L}", f"2×{Wd}", f"{2*L}+{2*Wd}", f"{P} × 1", f"{P}×{c}"]
        prev = []; print("== endless guard")
        for ln in chain:
            r = await pg.evaluate("([q, l, prev]) => window.__tt.judgeLine(l, q, prev)", [q, ln, prev]); print("  ", ln, "->", r["kind"], r.get("msg", "")[:50])
            if r["kind"] == "step": prev.append(ln)
        r = await pg.evaluate("([q, l, prev]) => window.__tt.judgeLine(l, q, prev)", [q, prev[0], prev]); print("   repeat", prev[0], "->", r["kind"], r.get("msg","")[:50])
        r = await pg.evaluate("([q, l, prev]) => window.__tt.judgeLine(l, q, prev)", [q, str(P*c), prev]); print("   answer after cap ->", r["kind"])
        print(f"\n{total-bad}/{total} as expected; errors {errs}"); await b.close()
asyncio.run(main())
