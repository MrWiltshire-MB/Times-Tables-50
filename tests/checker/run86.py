import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1366,"height":800}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,19,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        await pg.click("[data-gp='10B']"); await pg.wait_for_timeout(200)
        await pg.click(".calc-screen")
        out = lambda: pg.evaluate("() => [document.getElementById('calcExpr').textContent.trim(), document.getElementById('calcOut').innerText.replace(/\\n/g, '/')]")
        async def t(keys):
            for k in keys:
                if k in ("Enter","Escape","Backspace"): await pg.keyboard.press(k)
                else: await pg.keyboard.type(k)
            return await out()
        print("3/4:", await t(["Escape","3/4","Enter"]))
        await pg.screenshot(path=S+"/frac.png", clip={"x":960,"y":90,"width":230,"height":140})
        print("d:", await t(["d"]), "| d again:", await t(["d"]))
        print("x2:", await t(["*2","Enter"]))
        print("1/3+1/6:", await t(["Escape","1/3+1/6","Enter"]))
        print("6/3:", await t(["Escape","6/3","Enter"]))
        print("0.5x0.5:", await t(["Escape","0.5*0.5","Enter"]))
        print("2.5/4:", await t(["Escape","2.5/4","Enter"]))
        print("37.4/pi:", await t(["Escape","37.4/p","Enter"]), "| d:", await t(["d"]))
        print("-3/9:", await t(["Escape","-3/9","Enter"]))
        print("(2/3)^2:", await t(["Escape","2/3","^"]))
        print("5/0:", await t(["Escape","5/0","Enter"]))
        print("errors", errs); await b.close()
asyncio.run(main())
