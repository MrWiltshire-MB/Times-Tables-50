import asyncio, json, collections
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
GEN = """() => { const out = []; Math.random = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  for (const t of ['m10A','m10B','m10C','m10D','m10E','m10F','m10G','m10H','m10I','m10J','m10K','m10L']) for (let k = 0; k < 25; k++) for (const q of window.__tt.take(t, 20)) {
    if (!q.mwork) continue; const txt = q.html.replace(/<[^>]+>/g, ' ');
    const F = { mm: {cm: 0.1, m: 0.001}, cm: {mm: 10, m: 0.01}, m: {cm: 100, mm: 1000, km: 0.001}, km: {m: 1000}, mL: {L: 0.001}, L: {mL: 1000}, g: {kg: 0.001}, kg: {g: 1000}, t: {kg: 1000} };
    txt.replace(/(\\d+(?:\\.\\d+)?)\\s*(mm|cm|km|mL|kg|m|L|g|t)(?![A-Za-z²³])/g, (m0, v, u) => { Object.values(F[u] || {}).forEach(f => out.push([q, (f >= 1 ? v + ' × ' + f : v + ' ÷ ' + Math.round(1 / f)), t + ' ' + txt.replace(/\\d+(\\.\\d+)?/g, '#').slice(0, 60)])); return m0; });
  } return out; }"""
async def run(f):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/"+f); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(gen) => { const items = eval(gen)(); return items.map(([q, l, key]) => [key, l, window.__tt.judgeLine(l, q, []).kind]); }", GEN)
        await b.close(); return r
async def main():
    old, new = await run("harness-old.html"), await run("harness.html")
    diff = collections.Counter(); ex = {}
    for (k, l, a), (_, _, b2) in zip(old, new):
        if a != b2: diff[(k, a, b2)] += 1; ex[(k, a, b2)] = l
    for k, n in diff.most_common(): print(n, k, "e.g.", ex[k])
    print("total", len(old), "changed", sum(diff.values()))
asyncio.run(main())
