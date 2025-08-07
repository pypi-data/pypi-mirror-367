# selenium_web_automation_utils/logging_listener.py
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from selenium_web_automation_utils.logging_utils import logger
from selenium.common.exceptions import WebDriverException


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
        """
        Log real WebDriver exceptions, but ignore benign AttributeErrors
        about 'shape' or '__len__' being missing.
        """
        msg = clean_error_partition(exception)

        # Ignore these benign attribute‐lookup errors
        if isinstance(exception, AttributeError) and (
                "object has no attribute 'shape'" in msg or
                "object has no attribute '__len__'" in msg
        ):
            return

        try:
            current = driver.current_url
        except WebDriverException:
            current = "<couldn't fetch URL>"

        logger.error(
            "‼ WebDriver exception: %s at %s",
            msg,
            current
        )
