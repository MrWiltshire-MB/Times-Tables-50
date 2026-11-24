import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        import datetime, sys; TZ = datetime.timezone(datetime.timedelta(hours=11)); hh, dd = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (10, 24)
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1280,"height":900}, timezone_id="Australia/Melbourne"); await pg.clock.set_fixed_time(datetime.datetime(2026,11,dd,hh,0,tzinfo=TZ)); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        seed = """(rounds) => { const P = window.__tt.P(); let t = Date.now() - 1e8; P.history = rounds.map(([id, s, n]) => ({ d: t += 1e5, m: 'measurement', s, n, ms: 1, missed: [], parts: { ['m' + id]: [s, n] } })); window.__tt.save(); }"""
        await pg.evaluate(seed, [["10F",20,20],["10F",19,20],["10F",20,20],["10A",17,20]])
        await pg.click("#logo"); await pg.click("[data-open='topic:ch10']"); await pg.wait_for_timeout(200)
        print("10F tile:", (await pg.inner_text("#sub10F")).replace("\n"," | "))
        await pg.click("#sub10F", force=True); print("10F selectable?", await pg.get_attribute("#sub10F", "aria-pressed"))
        await pg.click("#topicAll"); print("select all ->", await pg.evaluate("() => window.__tt.store().settings.me.join(',')"))
        await pg.screenshot(path=S+"/plock.png")
        # green post chip for 10F -> goes to topic page, no round
        await pg.click("#logo"); await pg.wait_for_timeout(100)
        print("gp chip:", await pg.inner_text("[data-gp='10F']"))
        await pg.click("[data-gp='10F']"); await pg.wait_for_timeout(300)
        print("after tapping 10F chip: quiz", await pg.is_visible("#quiz"), "| topic page", await pg.evaluate("() => !document.getElementById('topicView').hidden"))
        # only one perfect -> not locked
        await pg.evaluate(seed, [["10F",20,20],["10F",19,20]]); await pg.click("#logo"); await pg.click("[data-open='topic:ch10']")
        print("one perfect, locked?", "Locked" in await pg.inner_text("#sub10F"))
        # all other parts 80%+ -> unlocked
        others = [[x,16,20] for x in ["10A","10B","10C","10D","10E","10G","10H","10I","10J","10K","10L"]]
        await pg.evaluate(seed, [["10F",20,20],["10F",20,20]] + others[:-1]); await pg.click("#logo"); await pg.click("[data-open='topic:ch10']")
        print("all but 10L:", (await pg.inner_text("#sub10F")).split("\n")[-1])
        await pg.evaluate(seed, [["10F",20,20],["10F",20,20]] + others); await pg.click("#logo"); await pg.click("[data-open='topic:ch10']")
        print("all 80%+ -> locked?", "Locked" in await pg.inner_text("#sub10F"))
        print(errs); await b.close()
asyncio.run(main())
