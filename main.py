import gi
import browser_data

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

class SimpleBrowser(Gtk.Window):
    def __init__(self):
        super().__init__(title="Refresh Browser")
        self.set_default_size(1024, 768)

        self.browser_data = browser_data.BrowserData()
        self.web_context = WebKit2.WebContext.get_default()
        self.browser_data.setup_context(self.web_context)

        # Create HeaderBar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "Refresh Browser"
        self.set_titlebar(header_bar)

        # Create Back button
        back_button = Gtk.Button()
        back_button.set_image(Gtk.Image.new_from_icon_name("go-previous", Gtk.IconSize.BUTTON))
        back_button.connect("clicked", self.on_back_clicked)
        header_bar.pack_start(back_button)

        # Create Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        refresh_button.connect("clicked", self.on_refresh_clicked)
        header_bar.pack_start(refresh_button)

        # Create More button with icon
        more_button = Gtk.MenuButton()
        icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        more_button.set_image(icon)

        # Create Popover for More button
        popover = Gtk.Popover()
        more_button.set_popover(popover)

        # Create ListBox for menu items
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        listbox = Gtk.ListBox()
        vbox.pack_start(listbox, True, True, 0)

        # Add ListBox items
        items = [("About Refresh", self.show_about),
                 ("Update", self.show_update),
                 ("Settings", self.show_settings),
                 ("Clear History", self.clear_history)]
        for item in items:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=item[0])
            row.add(label)
            row.set_activatable(True)
            row.connect("activate", item[1])
            listbox.add(row)

        listbox.show_all()
        vbox.show_all()
        popover.add(vbox)

        header_bar.pack_end(more_button)

        # Create Notebook for Tabs
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # Add initial tab
        self.add_new_tab("http://www.google.com")

        # Create New Tab button
        new_tab_button = Gtk.Button(label="+")
        new_tab_button.connect("clicked", self.on_new_tab_clicked)
        header_bar.pack_end(new_tab_button)

    def add_new_tab(self, url):
        scrolled_window = Gtk.ScrolledWindow()
        webview = WebKit2.WebView.new_with_context(self.web_context)
        webview.get_settings().set_user_agent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        webview.load_uri(url)
        scrolled_window.add(webview)

        tab_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tab_label = Gtk.Label(label="New Tab")
        close_button = Gtk.Button.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect("clicked", self.on_close_tab_clicked, scrolled_window)

        tab_label_box.pack_start(tab_label, True, True, 0)
        tab_label_box.pack_start(close_button, False, False, 0)
        tab_label_box.show_all()

        self.notebook.append_page(scrolled_window, tab_label_box)
        self.notebook.set_current_page(-1)
        scrolled_window.show_all()

        webview.connect("notify::title", self.on_title_changed, scrolled_window)
        webview.connect("load-changed", self.on_load_changed)

    def on_title_changed(self, webview, param, scrolled_window):
        title = webview.get_title()
        page_num = self.notebook.page_num(scrolled_window)
        tab_label_box = self.notebook.get_tab_label(scrolled_window)
        tab_label = tab_label_box.get_children()[0]
        tab_label.set_text(title)

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            uri = webview.get_uri()
            title = webview.get_title()
            self.browser_data.save_history(uri, title)

    def on_back_clicked(self, button):
        current_page = self.notebook.get_current_page()
        scrolled_window = self.notebook.get_nth_page(current_page)
        webview = scrolled_window.get_child().get_child()  # Get the WebView
        if webview.can_go_back():
            webview.go_back()

    def on_refresh_clicked(self, button):
        current_page = self.notebook.get_current_page()
        scrolled_window = self.notebook.get_nth_page(current_page)
        webview = scrolled_window.get_child().get_child()  # Get the WebView
        webview.reload()

    def on_new_tab_clicked(self, button):
        self.add_new_tab("http://www.google.com")

    def on_close_tab_clicked(self, button, scrolled_window):
        page_num = self.notebook.page_num(scrolled_window)
        self.notebook.remove_page(page_num)

    def show_about(self, widget):
        dialog = Gtk.MessageDialog(parent=self,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="Refresh Browser\nVersion 1.0")
        dialog.format_secondary_text("A simple web browser built with GTK and WebKitGTK.")
        dialog.run()
        dialog.destroy()

    def show_update(self, widget):
        dialog = Gtk.MessageDialog(parent=self,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="Update")
        dialog.format_secondary_text("No updates available.")
        dialog.run()
        dialog.destroy()

    def show_settings(self, widget):
        dialog = Gtk.MessageDialog(parent=self,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="Settings")
        dialog.format_secondary_text("No settings available.")
        dialog.run()
        dialog.destroy()

    def clear_history(self, widget):
        self.browser_data.clear_history()
        dialog = Gtk.MessageDialog(parent=self,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="Clear History")
        dialog.format_secondary_text("Browsing history has been cleared.")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = SimpleBrowser()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()