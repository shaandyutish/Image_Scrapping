import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from zipfile import ZipFile

# --- Extract image URLs from HTML ---
def get_image_links(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, 'html.parser')
        image_urls = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(url, src)
                image_urls.append(full_url)
        return image_urls
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return []

# --- Download selected images ---
def download_selected(images, selected):
    os.makedirs("downloads", exist_ok=True)
    paths = []
    for i in selected:
        try:
            img_url = images[i]
            ext = img_url.split('.')[-1].split("?")[0]
            filename = f"image_{i+1}.{ext}"
            path = os.path.join("downloads", filename)
            with open(path, 'wb') as f:
                f.write(requests.get(img_url).content)
            paths.append(path)
        except Exception as e:
            st.warning(f"Failed to download {img_url}: {e}")
    return paths

# --- Create ZIP ---
def make_zip(paths):
    zip_path = "downloaded_images.zip"
    with ZipFile(zip_path, 'w') as zipf:
        for path in paths:
            zipf.write(path, arcname=os.path.basename(path))
    return zip_path

# --- Streamlit App ---
st.title("🖼️ Universal Image Scraper (No Selenium)")

url = st.text_input("Enter any webpage URL")

if url:
    st.info("Fetching image previews...")
    images = get_image_links(url)
    
    if images:
        selected = st.multiselect("Select images to download", options=list(range(len(images))), format_func=lambda i: images[i])
        for i in selected:
            st.image(images[i], width=150, caption=f"Image {i+1}")
        
        if st.button("Download Selected"):
            downloaded = download_selected(images, selected)
            zip_file = make_zip(downloaded)
            with open(zip_file, "rb") as f:
                st.download_button("📥 Download ZIP", f, file_name="images.zip")
    else:
        st.warning("No images found.")
