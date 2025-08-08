import tkinter as tk
import cefpython3 as cef

class WebView(tk.Frame):
    def __init__(self, master, url="", **kwargs):
        super().__init__(master, **kwargs)
        self.browser = None
        self.embed_browser(url)
    
    def embed_browser(self, url):
        window_info = cef.WindowInfo()
        window_info.SetAsChild(self.winfo_id())
        self.browser = cef.CreateBrowserSync(window_info, url=url)
    
    def load_url(self, url):
        if self.browser:
            self.browser.LoadUrl(url)

class HTMLView(tk.Text):
    def render_html(self, html):
        self.delete("1.0", tk.END)
        self.insert("1.0", html)