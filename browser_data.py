import os
import json
from gi.repository import WebKit2

class BrowserData:
    def __init__(self):
        self.history_file = "browser_history.json"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                self.history = json.load(file)
        else:
            self.history = []

    def save_history(self, url, title):
        self.history.append({"url": url, "title": title})
        with open(self.history_file, "w") as file:
            json.dump(self.history, file)

    def clear_history(self):
        self.history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    def save_cookies(self, context):
        cookie_manager = context.get_cookie_manager()
        cookie_manager.set_persistent_storage("cookies.txt", WebKit2.CookiePersistentStorage.TEXT)
    
    def clear_cookies(self, context):
        cookie_manager = context.get_cookie_manager()
        cookie_manager.delete_all_cookies()

    def clear_cache(self, context):
        context.get_website_data_manager().clear(WebKit2.WebsiteData.ALL, 0, None, None)

    def setup_context(self, context):
        self.save_cookies(context)
