import os
import re
import json
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def extract_config_refresh_url(page_source):
    """
    Try to extract the Vimeo config_refresh_url from the page source.
    """
    match = re.search(r'"config_refresh_url":"(https://player\.vimeo\.com/video/[^"]+)"', page_source)
    if match:
        url = match.group(1).replace('\\u0026', '&').replace('\\/', '/')
        return url
    return None

def get_player_config_from_url(config_url, driver):
    """
    Use session cookies from Selenium to fetch the config JSON.
    """
    selenium_cookies = driver.get_cookies()
    s = requests.Session()
    for c in selenium_cookies:
        s.cookies.set(c['name'], c['value'])
    resp = s.get(config_url, headers={"Referer": "https://deeplizard.com/"})
    resp.raise_for_status()
    return resp.json()

def pick_hls_url(player_config):
    """
    List all available HLS stream CDNs, let the user pick one.
    """
    cdns = player_config["request"]["files"]["hls"]["cdns"]
    print("\nAvailable HLS streams (CDNs):")
    for i, (cdn, data) in enumerate(cdns.items()):
        print(f"{i}: {cdn} : {data['url']}")
    idx = input("Pick CDN index (default 0): ").strip() or "0"
    try:
        idx = int(idx)
    except Exception:
        idx = 0
    cdn_key = list(cdns.keys())[idx]
    hls_url = cdns[cdn_key]['url']
    return hls_url

def get_title(player_config):
    """
    Get a filename-safe title from the config JSON.
    """
    title = player_config.get("video", {}).get("title", "deeplizard_lesson")
    # Make safe for filenames
    safe_title = re.sub(r'[^A-Za-z0-9_\-\.]', "_", title)
    return safe_title

def download_with_ytdlp(hls_url, referer, filename):
    """
    Download the video with yt-dlp, passing referer and output filename.
    """
    print(f"\nStarting download with yt-dlp...\n")
    cmd = [
        "yt-dlp",
        "--referer", referer,
        "-o", filename + ".%(ext)s",  # Output filename (yt-dlp auto-selects ext)
        hls_url
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"\nDownload complete: {filename} (.mp4/.mkv depending on stream)")

def get_vimeo_iframe_src(driver):
    """
    Look for a Vimeo iframe on the page and return its src.
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        src = iframe.get_attribute("src")
        if src and "player.vimeo.com" in src:
            return src
    return None

def get_player_config_from_iframe(driver):
    """
    Use Selenium to extract window.playerConfig from the Vimeo iframe.
    """
    # Try for a few seconds in case playerConfig loads slowly
    import time
    for _ in range(10):
        try:
            config = driver.execute_script("return window.playerConfig || null;")
            if config:
                return config
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("window.playerConfig not found in iframe after waiting 10 seconds.")

def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    lesson_url = input("Paste Deeplizard lesson URL: ").strip()
    driver.get(lesson_url)
    print("\nPlease log in to Deeplizard in the opened browser window,")
    input("When you see the *video playing*, press Enter here...")

    # Try extracting config_refresh_url from main page
    page_source = driver.page_source
    config_url = extract_config_refresh_url(page_source)
    player_config = None

    if config_url:
        print(f"\nFound config URL: {config_url}")
        try:
            player_config = get_player_config_from_url(config_url, driver)
        except Exception as e:
            print("Error fetching playerConfig from config_url:", e)
    else:
        print("\nconfig_refresh_url not found in main page. Looking for Vimeo iframe...")
        iframe_src = get_vimeo_iframe_src(driver)
        if iframe_src:
            print(f"Found Vimeo iframe: {iframe_src}")
            print("Opening Vimeo iframe in new browser tab...")
            driver.get(iframe_src)
            try:
                player_config = get_player_config_from_iframe(driver)
            except Exception as e:
                print("Error extracting playerConfig from Vimeo iframe:", e)
                driver.quit()
                return
        else:
            print("Vimeo iframe not found. Cannot proceed.")
            driver.quit()
            return

    # ---- 3. Show available qualities ----
    title = get_title(player_config)
    print(f"\nLesson Title: {title}")

    try:
        streams = player_config["request"]["files"]["streams_avc"]
        print("\nAvailable Video Qualities:")
        for i, s in enumerate(streams):
            print(f"{i}: {s['quality']}p ({s['fps']}fps) profile={s['profile']}")
    except Exception:
        print("Could not parse available qualities, using HLS playlist instead.")

    # ---- 4. Get HLS playlist ----
    hls_url = pick_hls_url(player_config)
    print(f"\nHLS playlist URL:\n{hls_url}")

    # ---- 5. Download with yt-dlp ----
    referer = "https://deeplizard.com/"
    download_with_ytdlp(hls_url, referer, title)

    driver.quit()

if __name__ == "__main__":
    main()
