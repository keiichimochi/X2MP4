import streamlit as st
import yt_dlp
import os

# MP3フォルダが存在しない場合は作成
if not os.path.exists("mp3"):
    os.makedirs("mp3")

def download_and_convert_to_mp3(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        st.error(f"Error downloading {url}: {e}")
        return False

st.title("YouTube to MP3 Converter")
st.write("Enter up to 10 YouTube URLs to download and convert to MP3.")

urls = []
for i in range(10):
    url = st.text_input(f"URL {i+1}")
    if url:
        urls.append(url)

if st.button("Download MP3s"):
    for url in urls:
        st.write(f"Processing {url}...")
        success = download_and_convert_to_mp3(url, "mp3")
        if success:
            st.success(f"Downloaded and converted {url} to MP3")

st.write("MP3 files will be saved in the 'mp3' folder.")