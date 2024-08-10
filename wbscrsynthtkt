import tkinter as tk
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time

# Function to scrape the news using Selenium and BeautifulSoup
def fetch_news():
    print("Fetching news...")  # Debugging statement
    try:
        # Set up Selenium with Firefox WebDriver
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get("https://www.bbc.com/news")
        
        # Wait for the page to load fully
        time.sleep(20)  # Increased wait time to 20 seconds
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Fetching news articles based on the updated structure
        articles = soup.find_all('h2', {"data-testid": "card-headline"}, limit=3)
        news = []
        for article in articles:
            title = article.text if article else "No title available."
            # Fetching description from the next sibling paragraph (if it exists)
            description = article.find_next('p').text if article.find_next('p') else "No description available."
            news.append((title, description))
            print(f"Title: {title}")  # Print fetched title for debugging
            print(f"Description: {description}")
        
        # Close the browser
        driver.quit()
        
        return news
    except Exception as e:
        print(f"Failed to fetch news: {e}")  # Debugging statement
        return [("Error", f"Failed to fetch news: {e}")]

# Function to display the news in the GUI
def display_news():
    print("Displaying news...")  # Debugging statement
    
    # Clear any existing content in the news_frame
    for widget in news_frame.winfo_children():
        widget.destroy()
    
    # Fetch the news data
    news_data = fetch_news()
    
    # Display the news data
    for i, (title, description) in enumerate(news_data):
        title_label = tk.Label(news_frame, text=title, font=("Arial", 14, "bold"))
        title_label.grid(row=i*2, column=0, sticky="w", padx=10, pady=5)
        
        desc_label = tk.Label(news_frame, text=description, wraplength=600, justify="left")
        desc_label.grid(row=i*2+1, column=0, sticky="w", padx=10, pady=5)
    
    print("News displayed!")  # Debugging statement

# Set up the main window
root = tk.Tk()
root.title("Top News")
root.geometry("700x400")

# Create a frame to hold the news
news_frame = tk.Frame(root)
news_frame.pack(fill="both", expand=True)

# Add a "Connect" button to start fetching and displaying the news
connect_button = tk.Button(root, text="Connect", command=display_news, font=("Arial", 12))
connect_button.pack(pady=20)

# Start the GUI loop
root.mainloop()
