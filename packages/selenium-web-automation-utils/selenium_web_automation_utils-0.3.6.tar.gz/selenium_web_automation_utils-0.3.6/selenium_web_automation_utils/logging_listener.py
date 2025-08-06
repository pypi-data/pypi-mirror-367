# selenium_web_automation_utils/logging_listener.py
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from selenium_web_automation_utils.logging_utils import logger


def clean_error_partition(e: Exception) -> str:
    return str(e).partition("Stacktrace")[0].strip()


class LoggingListener(AbstractEventListener):

    def before_navigate_to(self, url: str, driver: WebDriver):
        logger.info("→ before_navigate_to: %s", url)

    def after_navigate_to(self, url: str, driver: WebDriver):
        logger.info("← after_navigate_to: %s (title=%r)",
                    driver.current_url, driver.title)

    def before_find(self, by, value, driver: WebDriver):
        logger.debug("→ before_find: %s=%s", by, value)

    def after_find(self, by, value, driver: WebDriver):
        logger.debug("← after_find: %s=%s", by, value)

    def before_click(self, element: WebElement, driver: WebDriver):
        snippet = element.get_attribute("outerHTML")[:100].replace("\n", "")
        logger.info("→ before_click on %s…", snippet)

    def before_execute_script(self, script: str, driver: WebDriver):
        logger.debug("→ before_execute_script: %s",
                     script[:100].replace("\n", " "))

    def after_execute_script(self, script: str, driver: WebDriver):
        logger.debug("← after_execute_script")

    def before_switch_to_frame(self, frame, driver: WebDriver):
        logger.info("→ before_switch_to_frame: %r", frame)

    def after_switch_to_frame(self, frame, driver: WebDriver):
        logger.info("← after_switch_to_frame: %r", frame)

    def before_alert_accept(self, driver: WebDriver):
        try:
            text = driver.switch_to.alert.text
        except Exception:
            text = "<no alert text>"
        logger.info("→ before_alert_accept: %s", text)

    def after_alert_accept(self, driver: WebDriver):
        logger.info("← after_alert_accept")

    def on_exception(self, exception, driver: WebDriver):
        try:
            current = driver.current_url
        except Exception:
            current = "<couldn't fetch URL>"
        logger.error(
            "‼ WebDriver exception at %s: %s",
            current,
            clean_error_partition(exception)
        )
        # # Walk the traceback to see if move_mouse_randomly is in the call stack
        # tb = exception.__traceback__
        # while tb:
        #     if tb.tb_frame.f_code.co_name in ["move_mouse_randomly"]:
        #         # Skip screenshot for mouse-move hiccups
        #         logger.warning("⚠ Skipping screenshot for move_mouse_randomly exception: %s", exception)
        #         return
        #     tb = tb.tb_next
        #
        # # Otherwise take a timestamped screenshot
        # ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        # filename = f"screenshot-{ts}.png"
        # try:
        #     driver.save_screenshot(filename)
        #     logger.info("✔ saved screenshot %s", filename)
        # except Exception as e:
        #     logger.error("✖ failed to save screenshot: %s", e)
        #
        # logger.error("‼ WebDriver exception: %s", exception)
