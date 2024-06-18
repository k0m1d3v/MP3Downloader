import tkinter as tk
from tkinter import filedialog, ttk
from ttkthemes import ThemedTk
from pytube import YouTube, exceptions
from moviepy.editor import AudioFileClip
import os
import threading

filesize = 0
download_queue = []


def browse_directory():
    directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, directory)


def progress_stream(stream, chunk, bytes_remaining):
    global filesize
    downloaded = filesize - bytes_remaining
    progress = (downloaded / filesize) * 100
    progress_bar["value"] = progress
    root.update_idletasks()  # update GUI


def download_video():
    global filesize
    url = download_queue[0]
    directory = directory_entry.get()
    try:
        yt = YouTube(url, on_progress_callback=progress_stream)
    except exceptions.PytubeError:
        status_label.config(text="Invalid URL or video cannot be downloaded.")
        return

    stream = yt.streams.filter(only_audio=True).first()

    filesize = stream.filesize
    progress_bar["maximum"] = 100

    status_label.config(text="Downloading...")
    stream.download(directory)
    status_label.config(text="Download complete.")
    status_label.config(text="Converting...")

    mp4_file = os.path.join(directory, stream.default_filename)
    mp3_file = os.path.join(directory, f"{yt.title}.mp3")
    AudioFileClip(mp4_file).write_audiofile(mp3_file)
    os.remove(mp4_file)
    status_label.config(text="Conversion complete.")

    progress_bar["value"] = 0
    download_queue.pop(0)  # remove the completed download from the queue
    if download_queue:  # start the next download if there is one
        threading.Thread(target=download_video, daemon=True).start()
    else:
        status_label.config(text="Ready for another download.")


def start_download():
    url = url_entry.get()
    download_queue.append(url)
    url_entry.delete(0, tk.END)  # Clear the URL field
    if len(download_queue) == 1:  # start download if this is the only item in the queue
        threading.Thread(target=download_video, daemon=True).start()


root = ThemedTk(theme="arc")
root.title("Mirko's Downloader")
root.geometry("500x120")

frame = ttk.Frame(root)
frame.pack()

url_label = ttk.Label(frame, text="YouTube URL:")
url_label.grid(row=0, column=0)

url_entry = ttk.Entry(frame, width=50)
url_entry.grid(row=0, column=1)

directory_label = ttk.Label(frame, text="Save to directory:")
directory_label.grid(row=1, column=0)

directory_entry = ttk.Entry(frame, width=50)
directory_entry.grid(row=1, column=1)

browse_button = ttk.Button(frame, text="Browse", command=browse_directory)
browse_button.grid(row=1, column=2)

download_button = ttk.Button(frame, text="Download", command=start_download)
download_button.grid(row=2, column=0, columnspan=3)

progress_bar = ttk.Progressbar(frame)
progress_bar.grid(row=3, column=0, columnspan=3)

status_label = ttk.Label(frame, text="Ready to download.")
status_label.grid(row=4, column=0, columnspan=3)

root.mainloop()
