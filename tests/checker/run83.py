import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
exec(open(S+"/run40.py").read().split("async def main")[0].split("TZ=")[1].split("\n",1)[1])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs=[]
        for W, H in [(1366, 768), (1280, 650), (1024, 600), (800, 900)]:
            pg = await b.new_page(viewport={"width":W,"height":H}); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.clock.set_fixed_time(datetime.datetime(2026,11,19,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
            await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
            await pg.evaluate("""() => { const p = window.__tt.P(), d = Date.now() - 9e6;
              [['10A',20],['10B',13],['10C',8]].forEach(([x, s], i) => p.history.push({ d: d + i, m: 'measurement', s, n: 20, ms: 1, missed: [], parts: { ['m' + x]: [s, 20] } })); window.__tt.save(); }""")
            await pg.reload(); await pg.wait_for_timeout(300)
            print(W, "home: side hidden", await pg.is_hidden("#quizSide"), "calc hidden", await pg.is_hidden("#calcBox"))
            await pg.click("[data-gp='10D']"); await pg.wait_for_timeout(200)
            for i in range(2): await answer(pg)
            side = await pg.locator("#quizSide").bounding_box(); card = await pg.locator("#quiz").bounding_box()
            calcv = await pg.is_visible("#calcBox"); cb = await pg.locator("#calcBox").bounding_box() if calcv else None
            print(f"  side {side and [round(side['x']), round(side['y']), round(side['width']), round(side['height'])]} | card x {round(card['x'])}-{round(card['x']+card['width'])} | calc visible {calcv} {cb and [round(cb['x']), round(cb['y']), round(cb['width']), round(cb['height'])]} | toggle {await pg.is_visible('#calcToggle')}")
            if side: print("  side fits screen:", side['y'] + side['height'] <= H, "| scroll needed:", await pg.evaluate("() => document.documentElement.scrollHeight > innerHeight"))
            await pg.screenshot(path=S+f"/side{W}.png")
            if W == 800:
                await pg.click("#calcToggle"); await pg.wait_for_timeout(100); print("  narrow calc open:", await pg.is_visible("#calcBox")); await pg.screenshot(path=S+"/side800calc.png")
            # calculator maths
            if await pg.is_visible("#calcBox"):
                async def keys(seq):
                    for k in seq: await pg.click(f"#calcKeys [data-k='{k}']")
                    return await pg.text_content("#calcOut")
                print("  2×π×8 =", await keys(["2","×","π","×","8","="]), "| ×2 =", await keys(["×","2","="]), "| C 37.4÷π=", await keys(["C","3","7",".","4","÷","π","="]),
                      "| C (3+4)×5=", await keys(["C","(","3","+","4",")","×","5","="]), "| 9 √:", await keys(["C","9","sqrt"]), "| 12 x²:", await keys(["C","1","2","sq"]), "| 5÷0=", await keys(["C","5","÷","0","="]), "| 1−−:", await keys(["C","1","−","×","2","="]))
            # answering still works with calc open
            await answer(pg); print("  q number:", await pg.text_content("#qnum"))
            await pg.close()
        print("errors", errs); await b.close()
asyncio.run(main())
