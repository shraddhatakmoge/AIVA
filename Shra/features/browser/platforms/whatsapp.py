import time
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from AIVA.Shra.features.browser.window_focus import bring_browser_to_front


class WhatsApp:
    def __init__(self, driver):
        self.driver = driver
        self.current_chat = None

    def get_url(self):
        return "https://web.whatsapp.com"

    # -------------------------------------------------
    # LOGIN
    # -------------------------------------------------
    def _is_logged_in(self):
        selectors = [
            "//button[@title='New chat']",
            "//span[@data-icon='new-chat-outline']",
            "//div[@contenteditable='true' and @role='textbox']",
            "//div[@contenteditable='true']",
        ]

        for xpath in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    try:
                        if el.is_displayed():
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
        return False

    def _wait_until_logged_in(self, timeout=60):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self._is_logged_in():
                return True
            time.sleep(0.5)
        return False

    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        if self._is_logged_in():
            return {"status": "success", "response": "Opened WhatsApp Web"}

        print("📱 Please scan QR code once...")

        if self._wait_until_logged_in(timeout=60):
            return {"status": "success", "response": "Opened WhatsApp Web"}

        return {
            "status": "login_required",
            "response": "Please scan the WhatsApp QR code to continue."
        }

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------
    def _click_element(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.1)
        except Exception:
            pass

        methods = [
            lambda: element.click(),
            lambda: ActionChains(self.driver).move_to_element(element).click().perform(),
            lambda: self.driver.execute_script("arguments[0].click();", element),
        ]

        for method in methods:
            try:
                method()
                time.sleep(0.2)
                return True
            except Exception:
                continue
        return False

    def _find_message_box(self, timeout=8):
        wait = WebDriverWait(self.driver, timeout)
        selectors = [
            "//footer//div[@contenteditable='true' and @role='textbox']",
            "//footer//*[@contenteditable='true' and @role='textbox']",
            "//footer//*[@contenteditable='true']",
        ]

        last_error = None
        for xpath in selectors:
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                print(f"✅ Message box found with: {xpath}")
                return element
            except Exception as e:
                last_error = e

        raise TimeoutException(f"Message box not found. Last error: {last_error}")

    def _click_new_chat(self, timeout=8):
        wait = WebDriverWait(self.driver, timeout)
        selectors = [
            "//button[@title='New chat']",
            "//span[@data-icon='new-chat-outline']/ancestor::button[1]",
            "//div[@title='New chat']",
            "//button[contains(@aria-label,'New chat')]",
        ]

        last_error = None
        for xpath in selectors:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                if self._click_element(el):
                    print(f"✅ New chat clicked with: {xpath}")
                    time.sleep(0.8)
                    return True
            except Exception as e:
                last_error = e

        raise TimeoutException(f"New chat button not found. Last error: {last_error}")

    def _find_new_chat_search_box(self, timeout=10):
        end_time = time.time() + timeout
        last_error = None

        selectors = [
            "//div[@role='dialog']//div[@contenteditable='true' and @role='textbox']",
            "//div[@role='dialog']//div[@contenteditable='true']",
            "(//div[@contenteditable='true' and @role='textbox' and not(ancestor::footer)])[1]",
            "(//div[@contenteditable='true' and not(ancestor::footer)])[1]",
            "//div[@contenteditable='true' and @data-tab='3' and not(ancestor::footer)]",
            "//div[@contenteditable='true' and @data-tab='2' and not(ancestor::footer)]",
        ]

        while time.time() < end_time:
            for xpath in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        try:
                            if el.is_displayed() and el.is_enabled():
                                print(f"✅ New chat search box found with: {xpath}")
                                return el
                        except Exception:
                            continue
                except Exception as e:
                    last_error = e
            time.sleep(0.4)

        raise TimeoutException(f"New chat search box not found. Last error: {last_error}")

    def _find_sidebar_search_box(self, timeout=10):
        """
        Robust approach:
        - collect all visible editable elements
        - ignore footer message box
        - choose the top-left visible textbox, which is typically the main sidebar search
        """
        end_time = time.time() + timeout
        last_error = None

        while time.time() < end_time:
            try:
                candidates = self.driver.find_elements(
                    By.XPATH,
                    "//div[@contenteditable='true' and not(ancestor::footer)] | "
                    "//input[not(ancestor::footer)] | "
                    "//textarea[not(ancestor::footer)]"
                )

                visible_candidates = []
                for el in candidates:
                    try:
                        if not el.is_displayed() or not el.is_enabled():
                            continue

                        rect = el.rect or {}
                        x = rect.get("x", 999999)
                        y = rect.get("y", 999999)
                        width = rect.get("width", 0)
                        height = rect.get("height", 0)

                        if width <= 0 or height <= 0:
                            continue

                        visible_candidates.append((y, x, el))
                    except Exception:
                        continue

                if visible_candidates:
                    visible_candidates.sort(key=lambda item: (item[0], item[1]))
                    chosen = visible_candidates[0][2]
                    print("✅ Sidebar search box found via visible editable element scan")
                    return chosen

            except Exception as e:
                last_error = e

            time.sleep(0.3)

        raise TimeoutException(f"Sidebar search box not found. Last error: {last_error}")

    def _focus_sidebar_search_box(self, timeout=10):
        """
        Click the chosen visible top-left editable element and reuse active element if possible.
        """
        search_box = self._find_sidebar_search_box(timeout=timeout)

        if not self._click_element(search_box):
            raise TimeoutException("Could not click sidebar search box.")

        time.sleep(0.3)

        try:
            active = self.driver.switch_to.active_element
            if active and active.is_displayed() and active.is_enabled():
                tag = (active.tag_name or "").lower()
                contenteditable = (active.get_attribute("contenteditable") or "").lower()
                if tag in ["input", "textarea"] or contenteditable == "true":
                    print("✅ Active element is usable for sidebar search")
                    return active
        except Exception:
            pass

        return search_box

    def _clear_box(self, element):
        element.click()
        time.sleep(0.1)
        element.send_keys(Keys.CONTROL, "a")
        time.sleep(0.1)
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)

    def _find_first_contact_result(self, timeout=8):
        wait = WebDriverWait(self.driver, timeout)
        selectors = [
            "(//div[@role='listitem'])[1]",
            "(//span[@title]/ancestor::div[@role='listitem'])[1]",
            "(//span[@title])[1]",
        ]

        last_error = None
        for xpath in selectors:
            try:
                el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                print(f"✅ First contact result found with: {xpath}")
                return el
            except Exception as e:
                last_error = e

        raise TimeoutException(f"First contact result not found. Last error: {last_error}")

    def _find_exact_contact_result(self, contact_name, timeout=8):
        end_time = time.time() + timeout
        last_error = None

        exact_xpaths = [
            f"//span[@title=\"{contact_name}\"]",
            f"//div[@role='listitem']//span[@title=\"{contact_name}\"]",
            f"//span[@title=\"{contact_name}\"]/ancestor::div[@role='listitem'][1]",
        ]

        while time.time() < end_time:
            for xpath in exact_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        try:
                            if el.is_displayed():
                                print(f"✅ Exact contact result found with: {xpath}")
                                return el
                        except Exception:
                            continue
                except Exception as e:
                    last_error = e
            time.sleep(0.4)

        print(f"⚠ Exact contact '{contact_name}' not found. Falling back to first result.")
        return self._find_first_contact_result(timeout=5)

    def _is_chat_open(self):
        try:
            self._find_message_box(timeout=3)
            return True
        except Exception:
            return False

    def _open_chat_by_contact_name(self, contact_name):
        print(f"🔎 Trying to open chat for: {contact_name}")

        if (
            self.current_chat
            and self.current_chat.strip().lower() == contact_name.strip().lower()
            and self._is_chat_open()
        ):
            print("✅ Chat already open, skipping contact search")
            return True

        try:
            search_box = self._focus_sidebar_search_box(timeout=10)
            self._clear_box(search_box)
            search_box.click()
            time.sleep(0.2)
            search_box.send_keys(contact_name)
            print("✅ Contact name typed in main WhatsApp search")
            time.sleep(1.5)

            result = self._find_exact_contact_result(contact_name, timeout=6)
            if self._click_element(result):
                print("✅ Contact result clicked from main search")
                time.sleep(1)

                if self._is_chat_open():
                    self.current_chat = contact_name
                    print("✅ Chat opened successfully via main search")
                    return True

        except Exception as e:
            print(f"⚠ Main search flow failed: {e}")

        return False

    # -------------------------------------------------
    # SEND MESSAGE
    # -------------------------------------------------
    def send_message(self, query):
        phone_number = query.get("phone_number")
        contact_name = query.get("contact_name")
        message = query.get("message")

        if not message:
            return {"status": "error", "response": "Message is required."}

        try:
            if not self._is_logged_in():
                print("📱 Please scan QR code once...")
                if not self._wait_until_logged_in(timeout=60):
                    bring_browser_to_front()
                    return {
                        "status": "login_required",
                        "response": "Please scan the WhatsApp QR code to continue."
                    }

            if phone_number:
                phone_number = "".join(ch for ch in str(phone_number) if ch.isdigit())
                encoded_message = quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"

                print(f"🔎 Opening phone chat: {phone_number}")
                self.driver.get(url)
                bring_browser_to_front()

                try:
                    message_box = self._find_message_box(timeout=10)
                    message_box.click()
                    time.sleep(0.2)
                    message_box.send_keys(Keys.ENTER)
                    print("✅ Message sent with ENTER")
                except Exception:
                    return {
                        "status": "error",
                        "response": f"Could not send message to {phone_number}"
                    }

                return {
                    "status": "success",
                    "response": f"Message sent to {phone_number}"
                }

            elif contact_name:
                print(f"🔎 Opening WhatsApp for contact: {contact_name}")
                bring_browser_to_front()

                if not self._wait_until_logged_in(timeout=10):
                    return {
                        "status": "login_required",
                        "response": "Please scan the WhatsApp QR code to continue."
                    }

                opened = self._open_chat_by_contact_name(contact_name)
                if not opened:
                    return {
                        "status": "error",
                        "response": f"Could not open contact '{contact_name}'."
                    }

                message_box = self._find_message_box(timeout=8)
                message_box.click()
                time.sleep(0.1)
                message_box.send_keys(message)
                print("✅ Message typed")
                time.sleep(0.1)
                message_box.send_keys(Keys.ENTER)
                print("✅ Message sent with ENTER")

                return {
                    "status": "success",
                    "response": f"Message sent to '{contact_name}'"
                }

            else:
                return {
                    "status": "error",
                    "response": "Either 'phone_number' or 'contact_name' is required."
                }

        except Exception as e:
            bring_browser_to_front()
            return {
                "status": "error",
                "response": f"WhatsApp send failed: {e}"
            }