import customtkinter as ctk
import os
import sys
import io
import subprocess
from PIL import Image

# [NEW: PyInstaller Windowed Mode Fix]
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

if sys.platform == 'win32':
    _original_popen_init = subprocess.Popen.__init__
    def _patched_popen_init(self, *args, **kwargs):
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        _original_popen_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = _patched_popen_init

# Configure FFmpeg Path
def setup_ffmpeg():
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
    locations = [
        os.path.join(script_dir, "tools", "ffmpeg.exe"),
        os.path.join(script_dir, "ffmpeg.exe"),
        os.path.join(script_dir, "bin", "ffmpeg.exe"),
        os.path.join(os.getcwd(), "tools", "ffmpeg.exe") 
    ]
    
    found_ffmpeg = None
    for p in locations:
        if os.path.exists(p):
            found_ffmpeg = p
            break
            
    if found_ffmpeg:
        ffmpeg_dir = os.path.dirname(found_ffmpeg)
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
            print(f"[Main] Added FFmpeg to PATH: {ffmpeg_dir}")

setup_ffmpeg()

# Import DownloadView
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from views.download_view import DownloadView

# Ensure high DPI awareness on Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Set default theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Studio0808 影音下載器 V20260727")
        self.geometry(f"{1100}x{750}")
        self.minsize(900, 650)
        
        # Apply Dark Title Bar (Windows 10/11)
        def set_dark_titlebar():
            try:
                import ctypes
                self.update() # Ensure window is drawn
                
                # Get the actual window handle
                HWND = ctypes.windll.user32.GetParent(self.winfo_id())
                
                # 1. Try setting Immersive Dark Mode (allows black title bar)
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 20, ctypes.byref(value), ctypes.sizeof(value))
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 19, ctypes.byref(value), ctypes.sizeof(value))
                
                # 2. Force Title Bar Background Color
                color = ctypes.c_int(0x001F1A18) 
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 35, ctypes.byref(color), ctypes.sizeof(color))
                
                # 3. Force Title Text Color to White
                text_color = ctypes.c_int(0x00FFFFFF)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 36, ctypes.byref(text_color), ctypes.sizeof(text_color))

            except Exception as e:
                print(f"Set dark titlebar failed: {e}")
                
        self.after(200, set_dark_titlebar)
        
        # Set Application Icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "app.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                self.iconbitmap(default=icon_path)
                self.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load application icon app.ico. Error: {e}")
        
        # Maximize window
        self.after(0, lambda: self.state('zoomed'))
        
        # Handle close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure grid layout (1x2) - 0 is sidebar, 1 is the main view
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Navigation Frame (Darker background for depth)
        self.navigation_frame = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color="#181A1F") 
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(2, weight=1) # Spacer at bottom
        
        # Menu Font
        try:
            self.menu_font = ctk.CTkFont(family="Microsoft JhengHei UI", size=16, weight="bold")
        except:
            self.menu_font = ctk.CTkFont(size=16, weight="bold")

        # Create Buttons
        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
        
        img = None
        icon_path = os.path.join(icons_dir, "download.png")
        if os.path.exists(icon_path):
            img = ctk.CTkImage(light_image=Image.open(icon_path), size=(22, 22))

        self.dl_btn = ctk.CTkButton(self.navigation_frame, corner_radius=8, height=45, border_spacing=10,
                            text=" 影音下載",
                            image=img,
                            compound="left",
                            fg_color="#00897B", # Active Color
                            text_color="white",
                            anchor="w", 
                            font=self.menu_font)
        
        self.dl_btn.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 2))

        # 2. Main View
        self.download_view = DownloadView(self, corner_radius=0, fg_color="transparent")
        self.download_view.grid(row=0, column=1, sticky="nsew")
        if hasattr(self.download_view, "on_enter"):
            self.download_view.on_enter()

    def on_closing(self):
        # Stop any background threads if needed
        if hasattr(self.download_view, "stop_download"):
            self.download_view.stop_download()
        self.destroy()

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Set Windows App ID to separate taskbar icon from generic python.exe
    try:
        import ctypes
        myappid = 'studio0808.downloader.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = App()
    app.mainloop()
