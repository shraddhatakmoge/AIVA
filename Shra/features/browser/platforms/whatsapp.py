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
                time.sleep(0.25)
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

                return element
            except Exception as e:
                last_error = e

        raise TimeoutException(f"Message box not found. Last error: {last_error}")

    def _clear_box(self, element):
        element.click()
        time.sleep(0.1)
        element.send_keys(Keys.CONTROL, "a")
        time.sleep(0.1)
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)

    def _find_sidebar_search_box(self, timeout=10):
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
    # UNREAD MESSAGE HELPERS
    # -------------------------------------------------
    def _click_chat_filter(self, filter_name, timeout=6):
        end_time = time.time() + timeout
        filter_name_lower = filter_name.strip().lower()
        last_error = None

        selectors = [
            f"//button[.//span[starts-with(normalize-space(), '{filter_name}')]]",
            f"//button[starts-with(normalize-space(.), '{filter_name}')]",
            f"//span[starts-with(normalize-space(), '{filter_name}')]/ancestor::button[1]",
            f"//*[self::button or ancestor::button][starts-with(normalize-space(.), '{filter_name}')]",
            f"//div[@role='button'][starts-with(normalize-space(.), '{filter_name}')]",
            f"//span[starts-with(normalize-space(), '{filter_name}')]/ancestor::*[@role='button'][1]",
        ]

        while time.time() < end_time:
            for xpath in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        try:
                            if not el.is_displayed() or not el.is_enabled():
                                continue

                            text = " ".join((el.text or "").split()).strip().lower()
                            if filter_name_lower == "all":
                                if not text.startswith("all"):
                                    continue
                            elif filter_name_lower == "unread":
                                if not text.startswith("unread"):
                                    continue

                            if self._click_element(el):

                                time.sleep(1.0)
                                return True
                        except Exception as e:
                            last_error = e
                            continue
                except Exception as e:
                    last_error = e

            time.sleep(0.4)

        print(f"⚠ Could not click chat filter '{filter_name}'. Last error: {last_error}")
        return False

    def _is_left_pane_candidate(self, element):
        try:
            if not element.is_displayed():
                return False

            rect = element.rect or {}
            x = rect.get("x", 0)
            y = rect.get("y", 0)
            width = rect.get("width", 0)
            height = rect.get("height", 0)

            if width < 120 or height < 30:
                return False

            viewport_width = self.driver.execute_script("return window.innerWidth") or 1400

            if x > (viewport_width * 0.55):
                return False

            if y < 120:
                return False

            return True
        except Exception:
            return False

    def _find_visible_chat_rows_via_xpath(self):
        selectors = [
            "//div[@role='listitem']",
            "//div[@data-testid='cell-frame-container']",
            "//div[@data-testid='chat-list-item']",
            "//span[@title]/ancestor::div[@role='listitem'][1]",
            "//span[@title]/ancestor::div[@data-testid='cell-frame-container'][1]",
            "//span[@title]/ancestor::div[@data-testid='chat-list-item'][1]",
            "//span[@title]/ancestor::div[3]",
            "//span[@title]/ancestor::div[4]",
            "//span[@title]/ancestor::div[5]",
            "//span[@title]/ancestor::div[6]",
        ]

        rows = []
        seen = set()

        for xpath in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    try:
                        if not self._is_left_pane_candidate(el):
                            continue

                        key = el.id
                        if key in seen:
                            continue

                        name = self._extract_chat_name_from_row(el)
                        if not name or name.lower() in {"all", "unread", "groups", "favourites", "favorites"}:
                            continue

                        seen.add(key)
                        rows.append(el)
                    except Exception:
                        continue
            except Exception:
                continue

        return rows

    def _find_visible_chat_rows_via_js(self):
        try:
            elements = self.driver.execute_script("""
                const results = [];
                const seen = new Set();
                const spans = Array.from(document.querySelectorAll('span[title]'));
                const maxX = window.innerWidth * 0.55;

                for (const span of spans) {
                    const title = (span.getAttribute('title') || '').trim();
                    if (!title) continue;

                    const bad = ['All', 'Unread', 'Groups', 'Favourites', 'Favorites'];
                    if (bad.includes(title)) continue;

                    let node = span;
                    for (let i = 0; i < 8 && node; i++) {
                        node = node.parentElement;
                        if (!node) break;

                        const r = node.getBoundingClientRect();
                        const style = window.getComputedStyle(node);

                        if (
                            r.width >= 120 &&
                            r.height >= 32 &&
                            r.left >= 0 &&
                            r.left <= maxX &&
                            r.top >= 120 &&
                            r.bottom <= window.innerHeight + 5 &&
                            style.display !== 'none' &&
                            style.visibility !== 'hidden'
                        ) {
                            if (!seen.has(node)) {
                                seen.add(node);
                                results.push(node);
                            }
                            break;
                        }
                    }
                }
                return results;
            """)

            return elements or []
        except Exception:
            return []

    def _find_visible_chat_rows(self):
        rows = []
        seen = set()

        for source_rows in [self._find_visible_chat_rows_via_xpath(), self._find_visible_chat_rows_via_js()]:
            for el in source_rows:
                try:
                    if not self._is_left_pane_candidate(el):
                        continue

                    key = el.id
                    if key in seen:
                        continue

                    name = self._extract_chat_name_from_row(el)
                    if not name or name.lower() in {"all", "unread", "groups", "favourites", "favorites"}:
                        continue

                    seen.add(key)
                    rows.append(el)
                except Exception:
                    continue

        try:
            rows.sort(key=lambda e: (e.rect or {}).get("y", 999999))
        except Exception:
            pass

        return rows

    def _extract_chat_name_from_row(self, row):
        selectors = [
            ".//span[@title]",
            ".//div[@dir='auto']//span",
            ".//span[contains(@class,'x1iyjqo2')]",
        ]

        for xpath in selectors:
            try:
                elements = row.find_elements(By.XPATH, xpath)
                for el in elements:
                    try:
                        text = (el.get_attribute("title") or el.text or "").strip()
                        if text:
                            return text
                    except Exception:
                        continue
            except Exception:
                continue

        try:
            text = " ".join((row.text or "").split()).strip()
            if text:
                return text.split("\n")[0].strip()
        except Exception:
            pass

        return "Unknown chat"

    def _open_first_unread_chat(self, timeout=10):
        end_time = time.time() + timeout

        while time.time() < end_time:
            rows = self._find_visible_chat_rows()
            print(f"🔎 Visible chat rows after filter: {len(rows)}")

            for i, row in enumerate(rows[:10], start=1):
                try:
                    chat_name = self._extract_chat_name_from_row(row)
                    print(f"   Row {i}: {chat_name}")

                    if self._click_element(row):
                        time.sleep(1.2)

                        if self._is_chat_open():
                            self.current_chat = chat_name
                            print(f"✅ Unread chat opened: {chat_name}")
                            return chat_name
                except Exception as e:
                    print(f"⚠ Failed clicking filtered row {i}: {e}")
                    continue

            time.sleep(0.5)

        return None

    def _extract_text_from_message_element(self, el):
        try:
            text_parts = el.find_elements(By.XPATH, ".//span[@dir='ltr'] | .//div[@dir='auto']")
            collected = []

            for part in text_parts:
                try:
                    t = (part.text or "").strip()
                    if t:
                        collected.append(t)
                except Exception:
                    continue

            if collected:
                text = "\n".join(collected).strip()
            else:
                text = (el.text or "").strip()

            text = " ".join(text.split()).strip()
            return text
        except Exception:
            return ""

    def _read_latest_unread_messages_from_open_chat(self, limit=2):
        divider_y = None

        divider_selectors = [
            "//*[contains(translate(normalize-space(.), 'UNREAD MESSAGE', 'unread message'), 'unread message')]",
            "//*[contains(translate(normalize-space(.), 'UNREAD MESSAGES', 'unread messages'), 'unread messages')]",
        ]

        for xpath in divider_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        divider_y = (el.rect or {}).get("y", None)
                        break
                if divider_y is not None:
                    break
            except:
                pass

        # 🔥 FIX: ignore broken divider
        if divider_y == 0:
            divider_y = None

        incoming = self.driver.find_elements(By.XPATH, "//div[contains(@class,'message-in')]")

        if not incoming:
            return []

        messages = []

        for el in incoming:
            try:
                y = (el.rect or {}).get("y", 0)

                if divider_y is not None and y <= divider_y:
                    continue

                text = self._extract_text_from_message_element(el)
                if text:
                    messages.append(text)
            except:
                continue

        # 🔥 ONLY LAST UNREAD MESSAGE
        if messages:
            return [messages[-1]]

        # fallback → last incoming only
        for el in reversed(incoming):
            text = self._extract_text_from_message_element(el)
            if text:
                return [text]

        return []

    def _read_last_messages_from_open_chat(self, limit=2):
        selectors = [
            "//div[contains(@class,'message-in')]",
            "//div[contains(@data-testid,'msg-container') and .//div[contains(@class,'message-in')]]",
            "//div[contains(@class,'focusable-list-item')][.//div[contains(@class,'message-in')]]",
        ]

        messages = []

        for xpath in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    for el in elements[-12:]:
                        text = self._extract_text_from_message_element(el)
                        if text:
                            messages.append(text)

                    if messages:
                        break
            except Exception:
                continue

        cleaned = []
        for msg in messages:
            msg = " ".join(msg.split())
            if msg and msg not in cleaned:
                cleaned.append(msg)

        return cleaned[-limit:]

    def _read_last_messages_from_current_chat(self, count=5):
        selectors = [
            "//div[contains(@class,'message-in')]",
            "//div[contains(@class,'message-out')]",
            "//div[contains(@data-testid,'msg-container')]",
            "//div[contains(@class,'focusable-list-item')]",
        ]

        collected = []

        for xpath in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if not elements:
                    continue

                for el in elements[-20:]:
                    try:
                        text = (el.text or "").strip()
                        if text:
                            text = " ".join(text.split())
                            if text and text not in collected:
                                collected.append(text)
                    except Exception:
                        continue

                if collected:
                    break

            except Exception:
                continue

        return collected[-count:]

    def _read_messages_from_contact(self, contact_name, count=5):
        opened = self._open_chat_by_contact_name(contact_name)
        if not opened:
            return {
                "status": "error",
                "response": f"Could not open contact '{contact_name}'."
            }

        messages = self._read_last_messages_from_current_chat(count=count)

        if not messages:
            return {
                "status": "error",
                "response": f"No readable messages found in chat '{contact_name}'."
            }

        formatted = " | ".join(
            [f"{i + 1}. {msg}" for i, msg in enumerate(messages)]
        )

        return {
            "status": "success",
            "response": f"Last {len(messages)} messages from {contact_name}: {formatted}"
        }

    # -------------------------------------------------
    # READ UNREAD MESSAGES
    # -------------------------------------------------
    def read_unread_messages(self, query=None):
        try:
            bring_browser_to_front()

            if not self._is_logged_in():
                if not self._wait_until_logged_in(timeout=60):
                    return {
                        "status": "login_required",
                        "response": "Please scan the WhatsApp QR code to continue."
                    }

            if not self._click_chat_filter("Unread", timeout=6):
                return {
                    "status": "error",
                    "response": "Could not click the Unread filter."
                }

            time.sleep(1.2)

            rows = self._find_visible_chat_rows()

            if not rows:
                self._click_chat_filter("All", timeout=3)
                return {"status": "success", "response": "No unread messages"}

            final_output = []
            seen_chats = set()  # 🔥 FIX: remove duplicates

            for row in rows:
                try:
                    chat_name = self._extract_chat_name_from_row(row)

                    # skip duplicates
                    if chat_name in seen_chats:
                        continue
                    seen_chats.add(chat_name)

                    if not self._click_element(row):
                        continue

                    time.sleep(1)

                    if not self._is_chat_open():
                        continue

                    self.current_chat = chat_name

                    messages = self._read_latest_unread_messages_from_open_chat()

                    if messages:
                        final_output.append(f"{chat_name}: {messages[0]}")

                except:
                    continue

            self._click_chat_filter("All", timeout=3)

            if not final_output:
                return {"status": "success", "response": "No unread messages"}

            return {
                "status": "success",
                "response": "\n".join(final_output)
            }

        except Exception as e:
            try:
                self._click_chat_filter("All", timeout=2)
            except:
                pass

            return {
                "status": "error",
                "response": f"WhatsApp unread read failed: {e}"
            }

    def read_messages(self, query=None):
        query = query or {}

        count = query.get("count", 5)
        unread_only = query.get("unread_only", False)
        contact_name = query.get("contact_name")

        try:
            bring_browser_to_front()

            if not self._is_logged_in():
                print("📱 Please scan QR code once...")
                if not self._wait_until_logged_in(timeout=60):
                    return {
                        "status": "login_required",
                        "response": "Please scan the WhatsApp QR code to continue."
                    }

            if unread_only:
                return self.read_unread_messages({"limit": count})

            if contact_name:
                return self._read_messages_from_contact(contact_name, count=count)

            if not self._is_chat_open():
                return {
                    "status": "error",
                    "response": "No WhatsApp chat is currently open."
                }

            messages = self._read_last_messages_from_current_chat(count=count)

            if not messages:
                return {
                    "status": "error",
                    "response": "No readable messages found in the current chat."
                }

            chat_name = self.current_chat or "current chat"

            formatted = " | ".join(
                [f"{i + 1}. {msg}" for i, msg in enumerate(messages)]
            )

            return {
                "status": "success",
                "response": f"Last {len(messages)} messages from {chat_name}: {formatted}"
            }

        except Exception as e:
            return {
                "status": "error",
                "response": f"WhatsApp read failed: {e}"
            }

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