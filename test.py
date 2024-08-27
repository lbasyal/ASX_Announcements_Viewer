import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json

# Initialize Selenium WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (without GUI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    # Create WebDriver with ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to fetch announcements for a given ticker
def get_announcements(ticker):
    url = f"https://www.asx.com.au/asx/1/company/{ticker}/announcements?count=20&market_sensitive=false"
    driver = init_driver()
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the page to load

        # Find the JSON data on the page
        pre_tag = driver.find_element(By.TAG_NAME, "pre")
        json_data = pre_tag.text

        # Parse the JSON data
        data = json.loads(json_data)

        # Extract relevant data from the JSON
        announcements = []
        trading_halt = False
        for announcement in data.get("data", []):
            header = announcement.get("header")
            if "Trading Halt" in header:
                trading_halt = True
            announcements.append({
                "header": header,
                "document_date": announcement.get("document_date"),
                "url": announcement.get("url"),
                "size": announcement.get("size")
            })

        return announcements, trading_halt

    except Exception as e:
        st.error(f"Error occurred: {e}")
        return [], False

    finally:
        driver.quit()

# Main function to run the Streamlit app
def main():
    st.title("ASX Announcements Viewer (lbasyal)")

    # List of ticker symbols
    tickers = ["AEE", "REZ", "1AE", "1MC", "NRZ"]

    # Fetch and display tickers with "Trading Halt" announcements
    st.subheader("Tickers with 'Trading Halt' Announcements")
    tickers_with_halt = []
    for ticker in tickers:
        _, trading_halt = get_announcements(ticker)
        if trading_halt:
            tickers_with_halt.append(ticker)

    if tickers_with_halt:
        st.write(f"Tickers with 'Trading Halt' Announcements: {', '.join(tickers_with_halt)}")
    else:
        st.write("No tickers with 'Trading Halt' Announcements found.")

    # User selection for ticker symbol
    selected_ticker = st.selectbox("Select a ticker symbol", tickers)

    # Fetch announcements for the selected ticker
    announcements, _ = get_announcements(selected_ticker)
    
    st.write(f"Displaying 20 most recent announcements for {selected_ticker}")
    st.write(pd.DataFrame(announcements))

if __name__ == "__main__":
    main()
