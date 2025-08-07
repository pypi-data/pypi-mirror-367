import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PhoneScraper:
    def __init__(self):
        self.data = []

    def scrape_konga(self, driver, base_url, max_pages=50):
        for num in range(1, max_pages + 1):
            url = f"{base_url}{num}"
            print(f"Scraping Konga page: {url}")
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "List_listItem__KlvU2"))
                )
                container = driver.find_elements(By.CLASS_NAME, "List_listItem__KlvU2")
            except Exception as e:
                print(f"Failed to load Konga products on page {num}: {e}")
                continue

            for item in container:
                name = self._safe_get_text_selenium(item, By.TAG_NAME, "h3")
                price = self._safe_get_text_selenium(item, By.CLASS_NAME, "shared_price__gnso_")
                review = self._safe_get_text_selenium(item, By.CLASS_NAME, "starRating_starRating__HbX_4")

                self.data.append({
                    "Source": "Konga",
                    "Name": name,
                    "Price": price,
                    "Review": review
                })

    def scrape_jumia(self, base_url="https://www.jumia.com.ng/catalog/?q=smart+phones&page={}", num_pages=50, delay=1.5):
        for page in range(1, num_pages + 1):
            url = base_url.format(page)
            print(f"Scraping Jumia page: {url}")
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to load Jumia page {page}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="prd")

            for article in articles:
                name = self._safe_get_text_bs4(article, "h3", "name")
                price = self._safe_get_text_bs4(article, "div", "prc")
                review = self._safe_get_text_bs4(article, "div", "rev")

                self.data.append({
                    "Source": "Jumia",
                    "Name": name,
                    "Price": price,
                    "Review": review
                })

            time.sleep(delay)

    def _safe_get_text_selenium(self, element, by, value):
        try:
            return element.find_element(by, value).text.strip()
        except:
            return "NA"

    def _safe_get_text_bs4(self, parent, tag, class_name):
        try:
            return parent.find(tag, class_=class_name).text.strip()
        except:
            return "NA"

    def to_dataframe(self):
        return pd.DataFrame(self.data)

    def to_csv(self, filename="phones_data.csv"):
        self.to_dataframe().to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def to_json(self, filename="phones_data.json"):
        self.to_dataframe().to_json(filename, orient="records", indent=4)
        print(f"Data saved to {filename}")

    def to_excel(self, filename="phones_data.xlsx"):
        self.to_dataframe().to_excel(filename, index=False)
        print(f"Data saved to {filename}")
