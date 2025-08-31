import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess

# --- Aynı: sabit indirme klasörü ---
download_folder = os.path.expanduser(r"~/Downloads/YouTube")
os.makedirs(download_folder, exist_ok=True)

# --- GUI ---
root = tk.Tk()
root.title("YouTube Downloader (basit)")
root.geometry("680x260")
root.resizable(False, False)
root.configure(bg="#FF0000")

tk.Label(root, text=f"İndirme klasörü: {os.path.abspath(download_folder)}").pack(anchor="w", padx=12, pady=(10, 0))

frm = tk.Frame(root, padx=12, pady=12 ,bg="#FF0000")
frm.pack(fill="x")

tk.Label(frm, text="YouTube URL:", bg="#FF0000", fg="black").grid(row=0, column=0, sticky="w")
url_entry = tk.Entry(frm, width=70)
url_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=(2, 8))
url_entry.focus()

status_var = tk.StringVar(value="Hazır.")
last_file_var = tk.StringVar(value="-")

tk.Label(frm, text="Durum:").grid(row=2, column=0, sticky="w")
status_lbl = tk.Label(frm, textvariable=status_var, anchor="w", justify="left")
status_lbl.grid(row=3, column=0, columnspan=3, sticky="we")

tk.Label(frm, text="Son indirilen:").grid(row=4, column=0, sticky="w", pady=(10, 0))
last_file_lbl = tk.Label(frm, textvariable=last_file_var, fg="#2a6", anchor="w", justify="left", wraplength=640)
last_file_lbl.grid(row=5, column=0, columnspan=3, sticky="we")

def open_folder():
    path = os.path.abspath(download_folder)
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Hata", f"Klasör açılamadı:\n{e}")

def start_download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Uyarı", "Lütfen bir YouTube URL'si gir.")
        return
    status_var.set("İndirme başlatılıyor…")
    download_btn.config(state="disabled")
    t = threading.Thread(target=download_worker, args=(url,), daemon=True)
    t.start()

# --- Aynı mantık: progress_hook sadece Label’a yazar ---
def make_progress_hook():
    def progress_hook(d):
        if d.get("status") == "downloading":
            pct = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            status_var.set(f"{pct} | {speed} | ETA {eta}")
            root.update_idletasks()
        elif d.get("status") == "finished":
            filepath = d.get("filename")
            if filepath:
                last_file_var.set(os.path.abspath(filepath))
                status_var.set("Birleştirme/son adımlar…")
                try:
                    os.startfile(os.path.abspath(download_folder))  # Windows’ta klasörü aç
                except Exception:
                    pass
    return progress_hook

def download_worker(url):
    # --- Aynı: ydl_opts çekirdeği korunuyor ---
    ydl_opts = {
        "format": "best",  # en iyi kalite video+ses
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
        "progress_hooks": [make_progress_hook()],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        status_var.set("Bitti ✅")
    except Exception as e:
        status_var.set("Hata!")
        messagebox.showerror("İndirme Hatası", str(e))
    finally:
        download_btn.config(state="normal")

btn_row = tk.Frame(root, padx=12, pady=6)
btn_row.pack(fill="x")
download_btn = tk.Button(btn_row, text="İndir",fg="red", width=14, height=2, command=start_download)
download_btn.pack(side="left")
open_btn = tk.Button(btn_row, text="Klasörü Aç",  width=14, command=open_folder,fg="red")
open_btn.pack(side="right")

root.bind("<Return>", lambda e: start_download())
root.mainloop()
