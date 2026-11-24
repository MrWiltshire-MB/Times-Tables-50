import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        dl=[]; pg.on("dialog", lambda d: (dl.append(d.message), asyncio.ensure_future(d.dismiss())))   # pop-ups never confirm, like inside Claude
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        await pg.evaluate("""() => { const P = window.__tt.P(), t = Date.now(); P.vouchers = [{r:'greenpost',d:t,code:'GP-A',used:false},{r:'greenpost',d:t,code:'GP-B',used:false},{r:'greenpost',d:t,code:'GP-C',used:false},{r:'freetime',d:t,code:'FT-D',used:false}]; window.__tt.save(); }""")
        await pg.click("[data-open='char']"); await pg.click("#home"); await pg.wait_for_timeout(200)
        used = lambda: pg.evaluate("() => window.__tt.P().vouchers.filter(v => v.used).map(v => v.code).join(' ')")
        btn = pg.locator("#myRewards [data-redeem]").nth(1)
        await btn.click(); print("1st tap:", await btn.inner_text(), "| used:", await used())
        await btn.click(); await pg.wait_for_timeout(200); print("2nd tap used:", await used())
        await pg.locator("#myRewards [data-redeem-all]").click(); print("all 1st:", await pg.locator("#myRewards [data-redeem-all]").inner_text())
        await pg.wait_for_timeout(4300); print("after 4s:", await pg.locator("#myRewards [data-redeem-all]").inner_text())
        await pg.locator("#myRewards [data-redeem-all]").click(); await pg.locator("#myRewards [data-redeem-all]").click(); await pg.wait_for_timeout(200)
        print("all given:", await used(), "| pop-ups:", dl, errs)
        await pg.evaluate("() => { const P = window.__tt.P(); P.vouchers.push({r:'greenpost',d:Date.now(),code:'GP-E',used:false}); window.__tt.save(); }")
        await pg.click("[data-open='rewards']"); await pg.wait_for_timeout(200)
        cb = pg.locator("#crBox [data-redeem]").first; t1 = await cb.inner_text(); await cb.click(); t2 = await pg.locator("#crBox [data-redeem]").first.inner_text()
        print("class rewards:", t1, "->", t2); await b.close()
asyncio.run(main())
