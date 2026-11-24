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
        await pg.click("[data-gp='10C']"); await pg.wait_for_timeout(200)
        async def k(x): await pg.click(f"#calcKeys [data-k='{x}']")
        async def disp(): return (await pg.text_content("#calcExpr")).strip(), await pg.text_content("#calcOut")
        for x in ["3","7",".","4","÷","π"]: await k(x)
        print("typing:", await disp())
        await k("="); print("after =:", await disp())
        await k("÷"); await k("2"); print("carry on:", await disp())
        await k("="); print("=:", await disp())
        await k("5"); print("new number:", await disp())
        await k("back"); print("back:", await disp())
        await k("C"); print("clear:", await disp())
        print("errors", errs); await b.close()
asyncio.run(main())
