class WhatsApp:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://web.whatsapp.com"

    def open(self):
        self.driver.get(self.get_url())
        return {
            "status": "success",
            "response": "Opened WhatsApp"
        }