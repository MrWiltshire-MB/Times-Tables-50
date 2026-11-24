import os  # teacher code comes from the TT_CODE environment variable (never stored in the repo)
import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1280,"height":900}, timezone_id="Australia/Melbourne"); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        print("hidden with none:", await pg.evaluate("() => document.getElementById('myRewards').hidden"))
        await pg.evaluate("""() => { const P = window.__tt.P(); const t = Date.now();
          P.vouchers = [{r:'greenpost',d:t-3e8,code:'GP-AAAA',used:false,auto:true,grp:'a'},{r:'greenpost',d:t-2e8,code:'GP-BBBB',used:false,auto:true,hwp:'hw2'},
            {r:'greenpost',d:t-1e8,code:'GP-CCCC',used:false},{r:'freetime',d:t,code:'FT-DDDD',used:false},{r:'greenpost',d:t-9e8,code:'GP-OLD1',used:true}];
          window.__tt.save(); }""")
        await pg.click("#logo") ; await pg.evaluate("() => document.querySelector('[data-open=\"char\"]').click()"); await pg.click("#home"); await pg.wait_for_timeout(200)
        print("home box:", (await pg.inner_text("#myRewards")).replace("\n"," | ")[:300])
        await pg.screenshot(path=S+"/rew1.png")
        await pg.click("#myRewards [data-redeem-all]"); await pg.fill("#ulPin",os.environ["TT_CODE"]); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(1500)
        print("after all:", (await pg.inner_text("#myRewards")).replace("\n"," | ")[:200], "| used:", await pg.evaluate("() => window.__tt.P().vouchers.map(v => v.code + ':' + v.used).join(' ')"))
        await pg.click("#myRewards [data-redeem]"); await pg.fill("#ulPin",os.environ["TT_CODE"]); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(1500)
        print("after single: hidden", await pg.evaluate("() => document.getElementById('myRewards').hidden"), "| progress stats:", errs)
        # class rewards view still lists with activate all
        await pg.evaluate("() => { const P = window.__tt.P(); P.vouchers.push({r:'greenpost',d:Date.now(),code:'GP-EEEE',used:false},{r:'greenpost',d:Date.now(),code:'GP-FFFF',used:false}); window.__tt.save(); }")
        await pg.click("[data-open='rewards']"); await pg.wait_for_timeout(200)
        print("class rewards:", (await pg.inner_text("#crBox .cr-mine")).replace("\n"," | ")[:160])
        await pg.click("#crBox [data-redeem-all]"); await pg.fill("#ulPin",os.environ["TT_CODE"]); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(1500)
        print("cr after all:", await pg.locator("#crBox .cr-mine").count(), errs)
        await pg.set_viewport_size({"width":390,"height":800}); await pg.click("#home"); await pg.evaluate("() => { const P = window.__tt.P(); P.vouchers.push({r:'greenpost',d:Date.now(),code:'GP-GGGG',used:false},{r:'greenpost',d:Date.now(),code:'GP-HHHH',used:false}); window.__tt.save(); }")
        await pg.click("#logo"); await pg.click("[data-open='char']"); await pg.click("#home"); await pg.wait_for_timeout(200); await pg.screenshot(path=S+"/rew2.png")
        await b.close()
asyncio.run(main())
