import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1280,"height":1000}, timezone_id="Australia/Melbourne"); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        allp = "Object.fromEntries(['A','B','C','D','E','F','G','H','I','J','K','L'].map(x => ['m10' + x, [4, 4]]))"
        add = lambda s: pg.evaluate("(s) => { const P = window.__tt.P(); P.history.push({ d: Date.now(), m: 'measurement', s, n: 50, ms: 1, missed: [], all: 1, parts: " + allp + " }); window.__tt.save(); return window.__tt.checkAutoPost(); }", s)
        print("44/50 ->", await add(44))
        print("45/50 ->", (await add(45) or {}).get("grpLabel"))
        print("then 49/50 ->", await add(49), "| then 50/50 ->", (await add(50) or {}).get("grpLabel"))
        await pg.click("[data-open='char']"); await pg.click("#home"); await pg.wait_for_timeout(200)
        print("card:", (await pg.inner_text("#gpParts")).replace("\n", " | ")[-160:])
        await pg.locator("#gpCard").screenshot(path=S+"/rgp.png")
        await pg.click("[data-gp='review']"); await pg.wait_for_timeout(300)
        print("review starts:", await pg.inner_text("#qnum"))
        print("mini:", (await pg.inner_text("#gpMini")).replace("\n"," | ")[:200])
        print(errs); await b.close()
asyncio.run(main())
