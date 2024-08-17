from yt_dlp import YoutubeDL

ydl_opts = {}
with YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=MvvrxdePk5Y'])