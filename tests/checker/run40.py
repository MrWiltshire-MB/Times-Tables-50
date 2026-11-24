import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
async def answer(pg, wrong=False):
    q = await pg.evaluate("() => { const q = window.__tt.qs()[window.__tt.idx()]; return {kind:q.kind, ans:q.ans, model:q.model||null, t:q.t}; }")
    if wrong:
        if q["kind"] == "choice": await pg.locator("#choices .choice").nth((q["ans"]+1) % 2).click()
        elif q["kind"] == "work": await pg.fill("#wInput", "1+1"); await pg.press("#wInput","Enter")
        else: await pg.fill("#answer", "99999"); await pg.click("#go")
        await pg.wait_for_timeout(50); return
    if q["kind"] == "choice": await pg.locator("#choices .choice").nth(q["ans"]).click()
    elif q["kind"] == "work":
        for line in q["model"]: await pg.fill("#wInput", line); await pg.press("#wInput","Enter"); await pg.wait_for_timeout(40)
    else: await pg.fill("#answer", str(q["ans"])); await pg.click("#go")
    await pg.wait_for_timeout(60)
    if await pg.locator("#nextBtn").count(): await pg.click("#nextBtn")
    await pg.wait_for_timeout(40)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(timezone_id="Australia/Melbourne", viewport={"width":1366,"height":1000}); pg = await ctx.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,5,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        print("GP card:", await pg.text_content("#gpParts"))
        await pg.locator("#gpCard").screenshot(path=S+"/gp2.png")
        # pretend 10A-10E done on their own at 80%+, then play 10F for real
        await pg.evaluate("""() => { const p = window.__tt.P(), d = Date.now() - 60000;
          ['10A','10B','10C','10D','10E'].forEach((x, i) => p.history.push({ d: d + i, m: 'measurement', s: 17, n: 20, ms: 1, missed: [], parts: { ['m' + x]: [17, 20] }, lc: 17 })); window.__tt.save(); }""")
        await pg.reload(); await pg.wait_for_timeout(300)
        await pg.click("[data-gp='10F']"); await pg.wait_for_timeout(150)
        # answer 10, then leave with Home; resume; first question after resume gets a wrong attempt to check it stays wrong
        for i in range(10): await answer(pg)
        await answer(pg, wrong=True)
        await pg.click("#home"); await pg.wait_for_timeout(150)
        print("resume card:", await pg.text_content("#resumeText"))
        await pg.reload(); await pg.wait_for_timeout(300)
        print("after reload:", await pg.text_content("#resumeText"))
        await pg.screenshot(path=S+"/resume.png")
        await pg.click("#resumeGo"); await pg.wait_for_timeout(150)
        print("resumed at:", await pg.text_content("#qnum"), "| strip:", await pg.evaluate("() => [...document.querySelectorAll('#strip .cell')].slice(9,12).map(c=>c.className)"))
        await answer(pg)  # correct the wrong one
        for i in range(9): await answer(pg)
        print("score:", await pg.text_content("#score"), "| reward GP:", "Green Post" in (await pg.text_content("#reward")), "|", (await pg.locator(".rw-unlock").all_text_contents())[-1:])
        await pg.click("#toHome"); await pg.wait_for_timeout(150)
        print("resume card hidden:", await pg.is_hidden("#resumeCard"), "| GP count:", await pg.text_content("#gpCount"))
        print("GP card now:", await pg.text_content("#gpParts"))
        # 'Save and finish later' button
        await pg.click("[data-gp='10G']"); await pg.wait_for_timeout(150); await answer(pg); await answer(pg)
        await pg.click("#pauseBtn"); await pg.wait_for_timeout(150); print("pause button:", await pg.text_content("#resumeText"))
        await pg.click("#resumeDrop"); await pg.click("#resumeDrop"); await pg.wait_for_timeout(100); print("thrown away:", await pg.is_hidden("#resumeCard"))
        await pg.click("[data-open=rewards]"); await pg.wait_for_timeout(100); print("rewards notes:", [t[:60] for t in await pg.locator("#crBox .lock-note p").all_text_contents()])
        print("errors", errs); await b.close()
asyncio.run(main())
