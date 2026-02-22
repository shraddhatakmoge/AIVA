class Gmail:

    def __init__(self, driver):
        self.driver = driver

    def get_url(self):
        return "https://mail.google.com"

    def open(self):
        self.driver.get(self.get_url())

        return {
            "status": "success",
            "response": "Opened Gmail"
        }