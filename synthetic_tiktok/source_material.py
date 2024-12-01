import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from typing import List

# TODO: Also crawl the main article text itself
def fetch_bbc(limit: int = 3) -> List[dict]:
    """_summary_

    Args:
        limit (int, optional): The amount of news articles to fetch fromn. Defaults to 3.

    Returns:
        List[dict]: A list containing news data, with the following keys:
                    "title": The title of the news piece
                    "description": The description of the news piece
                    "image_data": The path of the image
    """
    print("Fetching news...")
    try:
        # Initialize the Firefox driver
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get("https://www.bbc.com/news")

        # Wait for the page to load completely
        time.sleep(20)  # Consider replacing with WebDriverWait for better reliability

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find the top 3 news articles
        articles = soup.find_all('h2', {"data-testid": "card-headline"}, limit=3)
        news = []
        for article in articles:
            title = article.text.strip() if article else "No title available."
            description_tag = article.find_next('p')
            description = description_tag.text.strip() if description_tag else "No description available."

            # Attempt to find the associated image
            image_tag = article.find_previous('img')
            image_data = None
            if image_tag and 'src' in image_tag.attrs:
                image_url = image_tag['src']
                try:
                    driver.get(image_url)
                    time.sleep(2)  # Short wait to ensure image loads
                    image_data = driver.get_screenshot_as_png()
                except Exception as img_e:
                    print(f"Failed to fetch image: {img_e}")

            result = {
                "title": title,
                "description": description,
                "image_data": image_data
            }
            news.append(result)

        driver.quit()
        return news
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return [("Error", f"Failed to fetch news: {e}", None)]
    
