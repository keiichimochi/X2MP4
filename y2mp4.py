import streamlit as st
import yt_dlp
import os

# MP4フォルダが存在しない場合は作成
if not os.path.exists("mp4"):
    os.makedirs("mp4")

def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        st.error(f"Error downloading {url}: {e}")
        return False

st.title("YouTube to MP4 Converter")
st.write("Enter YouTube URL to download and convert to MP4.")

url = st.text_input("YouTube URL")

if st.button("Download MP4"):
    if url:
        st.write(f"Processing {url}...")
        success = download_video(url, "mp4")
        if success:
            st.success(f"Downloaded and converted {url} to MP4")
    else:
        st.error("Please enter a valid YouTube URL")

st.write("MP4 files will be saved in the 'mp4' folder.")