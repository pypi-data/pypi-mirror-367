import asyncio
import time
from io import BytesIO

from playwright.async_api import async_playwright, Playwright
from playwright._impl._errors import TimeoutError
import re
from x_model import init_db
from xync_client.loader import TORM
from xync_client.Abc.PmAgent import PmAgentClient
from enum import StrEnum


async def input_(page, code: str) -> None:
    for i in code:
        await page.keyboard.press(i)
        await page.wait_for_timeout(100)
    time.sleep(3)


async def fiveDigitCode(page, agent):
    sms_code = input("Введите код из SMS: ")
    for i in range(5):
        await page.locator(f'input[name="confirmPassword-{i}"]').fill(sms_code[i])
    passcode = input("Введите 5-значный код: ")
    await input_(page, passcode)
    time.sleep(1)
    await input_(page, passcode)
    agent.auth["pass"] = passcode
    await agent.save()


async def login_cart(page, number_cart: str, agent) -> None:
    await page.locator('button[aria-controls="tabpanel-card"]').click()
    await page.wait_for_selector('input[placeholder="Введите номер карты"]', timeout=10000)
    await page.locator('input[placeholder="Введите номер карты"]').fill(number_cart)
    await page.locator('button[type="submit"]').click()
    await fiveDigitCode(page, agent)
    cookies = await page.context.storage_state()
    agent.state = cookies
    await agent.save()


async def login_and_password(page, login: str, password: str, agent) -> None:
    await page.locator('input[autocomplete="login"]').fill(login)
    await page.locator('input[autocomplete="password"]').fill(password)
    await page.locator('button[data-testid="button-continue"]').click()
    await fiveDigitCode(page, agent)


async def logged(page, passcode: str) -> None:
    await page.wait_for_selector(".UFWVuux_h6LdkrisQYCk", timeout=10000)
    for i in passcode:
        await page.keyboard.press(i)
        await page.wait_for_timeout(100)


async def last_transaction(page, amounts: int, transactions: str) -> bool:
    transaction = await page.locator(".JsCdEfJ6").all_text_contents()
    amount = await page.locator(".ibtVVZxM.APTNeSaT").all_text_contents()
    cleaned_amount = int(re.sub(r"[^\d]", "", amount[0]))
    amount_ = cleaned_amount == amounts
    transaction_ = transaction[0].strip().upper() == transactions.strip().upper()
    return amount_ and transaction_


async def check_last_transaction(result: bool):
    if result:
        print("Платеж получен")
    else:
        print("Не получен")


class Client(PmAgentClient):
    class Pages(StrEnum):
        SEND = "https://online.sberbank.ru/CSAFront/index.do"
        LOGIN = "https://online.sberbank.ru/CSAFront/index.do"

    norm: str = "sber"
    pages: type(StrEnum) = Pages

    async def _login(self):
        page = self.page
        if card := self.agent.auth.get("card"):
            time.sleep(1)
            if await page.locator('button[aria-controls="tabpanel-card"]').is_visible():
                await login_cart(page, card, self.agent)
            else:
                await logged(page, self.agent.auth.get("pass"))

        elif login := self.agent.auth.get("login"):
            await page.wait_for_timeout(1500)
            if await page.locator('button[aria-controls="tabpanel-login"]').is_visible():
                await login_and_password(self.page, login, self.agent.auth.get("password"), self.agent)
                cookies = await page.context.storage_state()
                self.agent.state = cookies
                await self.agent.save()
            else:
                await logged(self.page, self.agent.auth.get("pass"))

    async def send(self, dest: str, amount: int, payment: str) -> tuple[int, bytes]:
        page = self.page
        if not page.url.startswith(self.pages.SEND):
            try:
                await page.goto(self.pages.SEND)
            except TimeoutError:
                await self._login()
        await page.locator("a#nav-link-payments").click()
        await page.locator(".sxZoARZF").click()
        await page.locator("input#text-field-1").fill(dest)
        await page.locator(".tMUGN6jK").click()
        if len(dest) < 15:
            await page.click('button[title="В другой банк по СБП"]')
            await page.fill("input#text-field-1", payment)
            await page.locator(".Fv3KdbZw").click()
            await page.wait_for_selector("#sbptransfer\\:init\\:summ", state="visible")
            await page.fill("#sbptransfer\\:init\\:summ", str(amount))
            await page.click(".zcSt16vp")
            sms_code = input("Введите код из SMS: ")
            await page.fill('input[autocomplete="one-time-code"]', sms_code)
            await page.click(".zcSt16vp")

        else:
            await page.wait_for_selector("#p2ptransfer\\:xbcard\\:amount", state="visible")
            await page.fill("#p2ptransfer\\:xbcard\\:amount", str(amount))
            await page.wait_for_selector("button.bjm6hnlx", state="visible")
            await page.wait_for_timeout(1000)
            await page.click('button:has-text("Продолжить")')
            await page.click("button.bjm6hnlx")
            await page.click("button.bjm6hnlx")
            sms_code = input("Введите код из SMS: ")
            await page.fill("input.MH9z5OYE", sms_code)
            await page.click("button.bjm6hnlx")

        time.sleep(2)
        async with page.expect_download() as download_info:
            await page.click(".TlmIYvgB")
        download = await download_info.value
        return 1, download  # первая цифра - ид транзакции, пока не важна

    async def check_in(self, amount: int, cur: str, tid: str | int = None) -> float | None:
        pass

    async def proof(self) -> bytes:
        pass


async def main(uid: int):
    _ = await init_db(TORM, True)
    playwright: Playwright = await async_playwright().start()
    sbr = Client(uid)
    await sbr.start(playwright, True)
    # тупо отправка файла
    file = open(__file__, "rb")
    await sbr.bot.send_document(uid, BytesIO(file.read()), caption="вот чек", file_name="sber.py")

    dest, amount, payment = "89308185958", 10, "Т-Банк"
    tid, pdf = await sbr.send(dest, amount, payment)
    await sbr.bot.send_document(uid, pdf, caption=f"Sberbank_transaction_{tid}.pdf")
    await sbr.stop()


if __name__ == "__main__":
    asyncio.run(main(1779829771))
