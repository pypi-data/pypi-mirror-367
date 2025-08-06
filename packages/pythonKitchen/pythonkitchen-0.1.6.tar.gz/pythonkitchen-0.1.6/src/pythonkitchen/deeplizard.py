from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

PARENT_URL = 'https://deeplizard.com'

course_urls = [
    "https://deeplizard.com/lesson/sda1ladzir",    # Chapter 1
    "https://deeplizard.com/lesson/dda1zridal",
    "https://deeplizard.com/lesson/dla1zrlida",
    "https://deeplizard.com/learn/video/RznKVRTFkBY",
    "https://deeplizard.com/learn/video/v5cngxo4mIg",
    "https://deeplizard.com/lesson/txta1lidrza",
    "https://deeplizard.com/learn/video/nyjbcRQ-uQ8",
    "https://deeplizard.com/lesson/gaa0ailzrd",
    "https://deeplizard.com/lesson/dia1aidrzl",
]

chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)

rows = []
for chapter_index, course_url in enumerate(course_urls, start=1):
    driver.get(course_url)
    try:
        wait = WebDriverWait(driver, 10)
        ol_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol.course-lessons")))
        # Extract each lesson in the chapter
        for a in ol_elem.find_elements(By.TAG_NAME, "a"):
            href = a.get_attribute('href')
            if href.startswith('/'):
                link = PARENT_URL + href
            else:
                link = href
            lesson_title = a.get_attribute('innerHTML').strip()
            lesson_name = href.split('/')[-1]
            rows.append([
                chapter_index,
                lesson_name,
                lesson_title,
                link
            ])
    except Exception as e:
        print(f"Could not extract lessons from {course_url}: {e}")

driver.quit()

csv_filename = '/Users/suhail/Desktop/deeplizard_lessons.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['chapter_index', 'name', 'description', 'link'])
    writer.writerows(rows)

print(f"Extracted {len(rows)} lessons to {csv_filename}")
