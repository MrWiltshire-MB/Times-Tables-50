import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1366,"height":800}, color_scheme="dark"); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,19,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        await pg.click("[data-gp='10B']"); await pg.wait_for_timeout(200)
        await pg.click(".calc-screen")
        clip = {"x":960,"y":90,"width":230,"height":150}
        for i, seq in enumerate(["5/", "5/3", "5/3+1/6", "(2+3)/4*p", "37.4/p/2"]):
            await pg.keyboard.press("Escape"); await pg.keyboard.type(seq); await pg.wait_for_timeout(50)
            await pg.screenshot(path=S+f"/ct{i}.png", clip=clip)
            print(seq, "->", (await pg.inner_text("#calcOut")).replace("\n","|"))
        await pg.keyboard.press("Enter"); print("= ->", (await pg.inner_text("#calcOut")).replace("\n","|"))
        await pg.keyboard.press("Escape"); await pg.keyboard.type("5/3"); await pg.keyboard.press("Enter"); print("5/3 = ->", (await pg.inner_text("#calcOut")).replace("\n","|"))
        print("errors", errs); await b.close()
asyncio.run(main())
