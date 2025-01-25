import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
from datetime import datetime
import threading
import re
from urllib.parse import urlparse, parse_qs


class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', padding=6, relief="flat", background="#2196f3")
        self.style.configure('TEntry', padding=6)
        self.style.configure('TProgressbar', thickness=20)

        self.create_widgets()

        # Download state
        self.downloading = False
        self.current_thread = None

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL Input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="Video URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Paste button
        ttk.Button(url_frame, text="Paste", command=self.paste_url).pack(side=tk.LEFT, padx=(5, 0))

        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        # Format selection
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=5)

        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="mp4")
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                         values=["mp4", "webm", "mp3"], width=10)
        self.format_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Quality selection
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=5)

        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                          values=["best", "1080p", "720p", "480p", "360p"], width=10)
        self.quality_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Audio only checkbox
        self.audio_only_var = tk.BooleanVar()
        self.audio_only_check = ttk.Checkbutton(options_frame, text="Audio Only",
                                                variable=self.audio_only_var,
                                                command=self.toggle_audio_only)
        self.audio_only_check.pack(pady=5)

        # Output directory
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=10)

        ttk.Label(output_frame, text="Save to:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=(5, 0))

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Download Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X)

        # Video info frame
        self.info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="10")
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.info_text = tk.Text(self.info_frame, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.download_button = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)

    def paste_url(self):
        url = self.root.clipboard_get()
        self.url_var.set(url)
        self.fetch_video_info()

    def browse_output(self):
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)

    def toggle_audio_only(self):
        if self.audio_only_var.get():
            self.format_var.set("mp3")
            self.format_combo.configure(state="disabled")
            self.quality_combo.configure(state="disabled")
        else:
            self.format_var.set("mp4")
            self.format_combo.configure(state="normal")
            self.quality_combo.configure(state="normal")

    def fetch_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            return

        def fetch():
            try:
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.root.after(0, lambda: self.update_video_info(info))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error fetching video info: {str(e)}"))

        threading.Thread(target=fetch, daemon=True).start()

    def update_video_info(self, info):
        self.info_text.delete(1.0, tk.END)
        info_text = f"Title: {info.get('title', 'N/A')}\n"
        info_text += f"Channel: {info.get('uploader', 'N/A')}\n"
        info_text += f"Duration: {info.get('duration_string', 'N/A')}\n"
        info_text += f"Views: {info.get('view_count', 'N/A'):,}\n"
        self.info_text.insert(tk.END, info_text)

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return

        self.downloading = True
        self.download_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.NORMAL)
        self.progress_var.set(0)

        ydl_opts = self.get_download_options()
        self.current_thread = threading.Thread(target=self.download_video, args=(url, ydl_opts))
        self.current_thread.daemon = True
        self.current_thread.start()

    def get_download_options(self):
        output_template = os.path.join(
            self.output_var.get(),
            '%(title)s.%(ext)s'
        )

        ydl_opts = {
            'outtmpl': output_template,
            'progress_hooks': [self.update_progress],
            'quiet': True,
            'no_warnings': True,
        }

        if self.audio_only_var.get():
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            format_str = 'bestvideo+bestaudio/best'
            if self.quality_var.get() != 'best':
                format_str = f'bestvideo[height<={self.quality_var.get()[:-1]}]+bestaudio/best'
            ydl_opts['format'] = format_str

        return ydl_opts

    def download_video(self, url, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self.download_complete)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Download error: {str(e)}"))

    def update_progress(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                self.progress_var.set(float(p))
            except ValueError:
                pass
            self.status_var.set(f"Downloading... {d.get('_percent_str', '0%')} at {d.get('_speed_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.status_var.set('Processing downloaded file...')

    def download_complete(self):
        self.downloading = False
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set("Download completed!")
        messagebox.showinfo("Success", "Download completed successfully!")

    def cancel_download(self):
        if self.downloading and self.current_thread:
            self.downloading = False
            self.status_var.set("Download cancelled")
            self.download_button.configure(state=tk.NORMAL)
            self.cancel_button.configure(state=tk.DISABLED)

    def show_error(self, message):
        self.downloading = False
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()