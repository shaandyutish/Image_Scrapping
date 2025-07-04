import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO

def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version="138.0.7204.92").install()),
        options=chrome_options
    )
    return driver

def get_all_images(url):
    driver = setup_driver()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    image_urls = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            full_url = urljoin(url, src)
            image_urls.add(full_url.split("?")[0])
    return list(image_urls)

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

def save_images(selected, image_urls):
    folder = "Downloaded_Images"
    os.makedirs(folder, exist_ok=True)
    for idx in selected:
        try:
            url = image_urls[idx]
            ext = url.split('.')[-1].split("?")[0]
            filename = f"image_{idx+1}.{ext}"
            with open(os.path.join(folder, filename), "wb") as f:
                f.write(requests.get(url).content)
        except Exception as e:
            st.error(f"Error downloading image {idx+1}: {e}")

# ---- Streamlit UI ----
st.title("🌐 Image Scraper & Downloader")
url = st.text_input("Enter the URL of the webpage")

if st.button("Fetch Images"):
    if url:
        st.info("Scraping images...")
        images = get_all_images(url)
        if not images:
            st.warning("No images found.")
        else:
            st.success(f"Found {len(images)} images")
            selected_indices = []
            for i, img_url in enumerate(images[:50]):
                img = download_image(img_url)
                if img:
                    if st.checkbox(f"Image {i+1}: {img_url}", key=i):
                        selected_indices.append(i)
                    st.image(img, width=150)
            if st.button("Download Selected"):
                save_images(selected_indices, images)
                st.success("Downloaded selected images to 'Downloaded_Images' folder.")
    else:
        st.error("Please enter a valid URL.")
