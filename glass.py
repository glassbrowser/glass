import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, WebKit2, GLib, Gio

class BrowserTab:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)  # Changed orientation to HORIZONTAL
        self.webview = WebKit2.WebView()
        self.webview.connect('notify::title', self.on_title_changed)
        self.webview.connect('notify::uri', self.on_uri_changed)  # Connect to uri changed event
        self.box.pack_start(self.webview, True, True, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.box)
        self.label = Gtk.Label(label="New Tab")
        self.parent_window.notebook.append_page(self.scrolled_window, self.label)

        self.current_uri = ""

    def on_title_changed(self, webview, event):
        page_title = webview.get_title()
        self.label.set_text(page_title)

    def on_uri_changed(self, webview, event):
        self.current_uri = webview.get_uri()
        self.parent_window.update_search_entry(self.current_uri)  # Notify the parent window to update the search entry

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Glass Browser")
        self.set_default_size(800, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(button_box, False, False, 0)

        back_button = Gtk.Button()
        back_icon = Gio.ThemedIcon(name="go-previous-symbolic")
        back_image = Gtk.Image.new_from_gicon(back_icon, Gtk.IconSize.BUTTON)
        back_button.add(back_image)
        back_button.connect("clicked", self.on_back_button_clicked)
        button_box.pack_start(back_button, False, False, 0)

        forward_button = Gtk.Button()
        forward_icon = Gio.ThemedIcon(name="go-next-symbolic")
        forward_image = Gtk.Image.new_from_gicon(forward_icon, Gtk.IconSize.BUTTON)
        forward_button.add(forward_image)
        forward_button.connect("clicked", self.on_forward_button_clicked)
        button_box.pack_start(forward_button, False, False, 0)

        reload_button = Gtk.Button()
        reload_icon = Gio.ThemedIcon(name="view-refresh-symbolic")
        reload_image = Gtk.Image.new_from_gicon(reload_icon, Gtk.IconSize.BUTTON)
        reload_button.add(reload_image)
        reload_button.connect("clicked", self.on_reload_button_clicked)
        button_box.pack_start(reload_button, False, False, 0)

        close_tab_button = Gtk.Button()  # Close tab button
        close_tab_icon = Gio.ThemedIcon(name="window-close-symbolic")
        close_tab_image = Gtk.Image.new_from_gicon(close_tab_icon, Gtk.IconSize.BUTTON)
        close_tab_button.add(close_tab_image)
        close_tab_button.connect("clicked", self.on_close_tab_button_clicked)
        button_box.pack_end(close_tab_button, False, False, 0)

        new_tab_button = Gtk.Button()
        new_tab_icon = Gio.ThemedIcon(name="tab-new-symbolic")
        new_tab_image = Gtk.Image.new_from_gicon(new_tab_icon, Gtk.IconSize.BUTTON)
        new_tab_button.add(new_tab_image)
        new_tab_button.connect("clicked", self.on_new_tab_button_clicked)
        button_box.pack_end(new_tab_button, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("activate", self.on_search_entry_activate)
        button_box.pack_start(self.search_entry, True, True, 0)

        self.notebook = Gtk.Notebook()
        vbox.pack_start(self.notebook, True, True, 0)

        self.set_border_width(10)
        self.tabs = []
        self.add_new_tab()

    def add_new_tab(self, url="https://searxng.no-logs.com"):
        tab = BrowserTab(self)
        self.tabs.append(tab)
        self.notebook.show_all()
        if url:
            tab.webview.load_uri(url)

    def on_new_tab_button_clicked(self, button):
        self.add_new_tab()

    def on_bookmark_button_clicked(self, button):
        current_tab = self.get_current_tab()
        if current_tab:
            page_title = current_tab.webview.get_title()
            page_uri = current_tab.webview.get_uri()
            if page_title and page_uri:
                bookmark_dialog = Gtk.MessageDialog(
                    parent=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK_CANCEL,
                    text=f"Add Bookmark: {page_title}",
                )
                bookmark_dialog.format_secondary_text(page_uri)
                response = bookmark_dialog.run()
                if response == Gtk.ResponseType.OK:
                    self.save_bookmark(page_title, page_uri)
                bookmark_dialog.destroy()


    def on_search_entry_activate(self, entry):
        text = entry.get_text()
        current_tab = self.get_current_tab()

        if current_tab:
            webview = current_tab.webview
            if text.startswith("http://") or text.startswith("https://"):
                webview.load_uri(text)
            else:
                search_url = "https://searxng.no-logs.com/search?q=" + GLib.uri_escape_string(text, None, True)
                webview.load_uri(search_url)

    def get_current_tab(self):
        page_num = self.notebook.get_current_page()
        if page_num >= 0:
            return self.tabs[page_num]
        return None

    def on_back_button_clicked(self, button):
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.webview.go_back()

    def on_forward_button_clicked(self, button):
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.webview.go_forward()

    def on_reload_button_clicked(self, button):
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.webview.reload()

    def on_close_tab_button_clicked(self, button):
        current_tab = self.get_current_tab()
        if current_tab:
            tab_num = self.notebook.page_num(current_tab.scrolled_window)
            self.notebook.remove_page(tab_num)
            self.tabs.remove(current_tab)

    def update_search_entry(self, uri):
        self.search_entry.set_text(uri)  # Update the search entry with the current tab's URI

    def on_tab_switched(self, notebook, page, page_num):
        current_tab = self.tabs[page_num]
        if current_tab:
            current_uri = current_tab.webview.get_uri()
            self.update_search_entry(current_uri)

    def run(self):
        self.connect("destroy", Gtk.main_quit)
        self.notebook.connect("switch-page", self.on_tab_switched)  # Connect to the switch-page signal
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    win = MainWindow()
    win.run()
