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
        self.current_chat = None  # ADDED: cache last opened chat

    def get_url(self):
        return "https://web.whatsapp.com"

    # -------------------------------------------------
    # LOGIN
    # -------------------------------------------------
    def _is_logged_in(self):
        selectors = [
            "//div[@aria-label='Search input textbox']",
            "//button[@title='New chat']",
            "//span[@data-icon='new-chat-outline']",
            "//div[@contenteditable='true' and @data-tab='3']",
        ]

        for xpath in selectors:
            try:
                self.driver.find_element(By.XPATH, xpath)
                return True
            except NoSuchElementException:
                continue
        return False

    def _wait_until_logged_in(self, timeout=60):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self._is_logged_in():
                return True
            time.sleep(0.5)  # MODIFIED: reduced from 1 sec
        return False

    def open(self):
        self.driver.get(self.get_url())
        bring_browser_to_front()

        WebDriverWait(self.driver, 15).until(  # MODIFIED: reduced from 30
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
            time.sleep(0.1)  # MODIFIED: reduced from 0.2
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
                time.sleep(0.2)  # MODIFIED: reduced from 1
                return True
            except Exception:
                continue
        return False

    def _find_message_box(self, timeout=5):  # MODIFIED: reduced from 20
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

    def _click_new_chat(self, timeout=5):  # MODIFIED: reduced from 15
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
                    return True
            except Exception as e:
                last_error = e

        raise TimeoutException(f"New chat button not found. Last error: {last_error}")

    def _find_new_chat_search_box(self, timeout=5):  # MODIFIED: reduced from 15
        wait = WebDriverWait(self.driver, timeout)

        # This search appears after clicking "New chat"
        selectors = [
            "//div[@role='dialog']//div[@contenteditable='true' and @role='textbox']",
            "//div[@role='dialog']//div[@contenteditable='true']",
            "(//div[@contenteditable='true' and @role='textbox'])[1]",
        ]

        last_error = None
        for xpath in selectors:
            try:
                el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                print(f"✅ New chat search box found with: {xpath}")
                return el
            except Exception as e:
                last_error = e

        raise TimeoutException(f"New chat search box not found. Last error: {last_error}")

    def _clear_box(self, element):
        element.click()
        time.sleep(0.1)  # MODIFIED
        element.send_keys(Keys.CONTROL, "a")
        time.sleep(0.1)  # MODIFIED
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)  # MODIFIED: reduced from 0.8

    def _find_first_contact_result(self, timeout=5):  # MODIFIED: reduced from 10
        wait = WebDriverWait(self.driver, timeout)
        selectors = [
            "(//div[@role='dialog']//div[@role='listitem'])[1]",
            "(//div[@role='listitem'])[1]",
            "(//span[@title]/ancestor::div[@role='listitem'][1])[1]",
            "(//div[contains(@aria-label,'Search results')]//div[@role='listitem'])[1]",
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

    def _is_chat_open(self):
        try:
            self._find_message_box(timeout=3)  # MODIFIED: reduced from 5
            return True
        except Exception:
            return False

    def _open_chat_by_contact_name(self, contact_name):
        print(f"🔎 Trying to open chat for: {contact_name}")

        # ADDED: if same chat is already open, skip search
        if (
            self.current_chat
            and self.current_chat.strip().lower() == contact_name.strip().lower()
            and self._is_chat_open()
        ):
            print("✅ Chat already open, skipping contact search")
            return True

        # Step 1: click New Chat
        self._click_new_chat()

        # Step 2: search contact in new chat popup/panel
        search_box = self._find_new_chat_search_box()
        self._clear_box(search_box)

        # MODIFIED: removed duplicate _find_new_chat_search_box() call
        search_box.click()
        time.sleep(0.1)
        search_box.send_keys(contact_name)
        print("✅ Contact name typed in NEW CHAT search")
        time.sleep(0.5)  # MODIFIED: reduced from 2

        # Step 3: click first result
        first_result = self._find_first_contact_result(timeout=5)
        if not self._click_element(first_result):
            return False

        print("✅ First contact result clicked")
        time.sleep(0.4)  # MODIFIED: reduced from 2

        # Step 4: verify actual chat opened
        if self._is_chat_open():
            self.current_chat = contact_name  # ADDED
            print("✅ Chat opened successfully")
            return True

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

            # -------------------------------------------------
            # SEND BY PHONE NUMBER
            # -------------------------------------------------
            if phone_number:
                phone_number = "".join(ch for ch in str(phone_number) if ch.isdigit())
                encoded_message = quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"

                print(f"🔎 Opening phone chat: {phone_number}")
                self.driver.get(url)
                bring_browser_to_front()

                try:
                    message_box = self._find_message_box(timeout=8)  # MODIFIED
                    message_box.click()
                    time.sleep(0.1)
                    message_box.send_keys(Keys.ENTER)  # MODIFIED: direct send instead of waiting for send button
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

            # -------------------------------------------------
            # SEND BY CONTACT NAME
            # -------------------------------------------------
            elif contact_name:
                print(f"🔎 Opening WhatsApp for contact: {contact_name}")
                bring_browser_to_front()

                # MODIFIED: removed self.driver.get(self.get_url())
                # MODIFIED: removed unnecessary time.sleep(2)

                if not self._wait_until_logged_in(timeout=10):  # MODIFIED: reduced from 30
                    return {
                        "status": "login_required",
                        "response": "Please scan the WhatsApp QR code to continue."
                    }

                opened = self._open_chat_by_contact_name(contact_name)
                if not opened:
                    return {
                        "status": "error",
                        "response": f"Could not open contact '{contact_name}' from New Chat search."
                    }

                message_box = self._find_message_box(timeout=5)  # MODIFIED: reduced from 15
                message_box.click()
                time.sleep(0.1)  # MODIFIED: reduced from 0.4
                message_box.send_keys(message)
                print("✅ Message typed")
                time.sleep(0.1)  # MODIFIED: reduced from 0.8

                # MODIFIED: removed slow send-button wait, send directly with ENTER
                message_box.send_keys(Keys.ENTER)
                print("✅ Message sent with ENTER")

                return {
                    "status": "success",
                    "response": f"Message sent to first New Chat result for '{contact_name}'"
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