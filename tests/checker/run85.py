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
        # find a true/false question so 1/2 keys matter
        await pg.click("[data-gp='10B']"); await pg.wait_for_timeout(200)
        disp = lambda: pg.evaluate("() => [document.getElementById('calcExpr').textContent.trim(), document.getElementById('calcOut').textContent]")
        print("hint before:", await pg.text_content("#calcHint"))
        await pg.click(".calc-screen"); await pg.wait_for_timeout(50)
        print("hint after click:", await pg.text_content("#calcHint"), "| focused in calc:", await pg.evaluate("() => document.getElementById('calcBox').contains(document.activeElement)"))
        await pg.keyboard.type("2"); await pg.keyboard.press("Shift+8"); await pg.keyboard.type("p*8"); print("typed:", await disp())
        await pg.keyboard.press("Enter"); print("Enter:", await disp())
        await pg.keyboard.type("/2="); print("/2=:", await disp())
        await pg.keyboard.press("Escape"); await pg.keyboard.type("(3+4)x5"); await pg.keyboard.press("Backspace"); await pg.keyboard.type("6"); await pg.keyboard.press("Enter"); print("(3+4)x6:", await disp())
        await pg.keyboard.type("1"); print("1 typed (no choice picked):", await disp(), "| q still unanswered:", await pg.evaluate("() => document.getElementById('feedback').textContent === ''"))
        # click a calc button then type
        await pg.click("#calcKeys [data-k='9']"); await pg.keyboard.type("+1"); await pg.keyboard.press("Enter"); print("button then type:", await disp())
        # click into the answer box: typing goes there, not to the calculator
        inp = "#wInput" if await pg.locator("#wInput").count() else "#answer"
        if await pg.is_visible(inp):
            await pg.click(inp); await pg.keyboard.type("12"); print("answer box got:", await pg.input_value(inp), "| calc:", await disp(), "| hint:", await pg.text_content("#calcHint"))
        await pg.locator("#calcBox").screenshot(path=S+"/calcfocus.png")
        print("errors", errs); await b.close()
asyncio.run(main())
