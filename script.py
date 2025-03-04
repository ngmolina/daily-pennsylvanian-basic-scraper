"""
Scrapes headlines from multiple sections of The Daily Pennsylvanian website and saves them to a 
JSON file that tracks headlines over time.
"""

import os
import sys
import json
from datetime import datetime

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_data_point():
    """
    Scrapes headlines from multiple sections of The Daily Pennsylvanian website.

    Returns:
        dict: Dictionary containing headlines from different sections.
              Returns an empty dict if the scraping fails completely.
    """
    headers = {
        "User-Agent": "cis3500-scraper"
    }
    
    # Initialize results dictionary
    results = {
        "main_headline": "",
        "news_headline": "",
        "sports_headline": "",
        "opinion_headline": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M%p")
    }
    
    try:
        # Make request to the homepage
        loguru.logger.info(f"Making request to The Daily Pennsylvanian homepage")
        req = requests.get("https://www.thedp.com", headers=headers, timeout=30)
        loguru.logger.info(f"Request URL: {req.url}")
        loguru.logger.info(f"Request status code: {req.status_code}")
        
        if not req.ok:
            loguru.logger.error(f"Request failed with status code: {req.status_code}")
            return results
            
        # Parse the HTML content
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        
        # Try to extract the main headline (original functionality)
        try:
            loguru.logger.info("Attempting to extract main headline")
            main_headline = soup.find("a", class_="frontpage-link")
            if main_headline:
                results["main_headline"] = main_headline.text.strip()
                loguru.logger.info(f"Main headline: {results['main_headline']}")
        except Exception as e:
            loguru.logger.error(f"Failed to extract main headline: {e}")
        
        # Try to extract the top news headline
        try:
            loguru.logger.info("Attempting to extract top news headline")
            # First approach: look for the news section by its class
            news_section = soup.find("div", class_="col-sm-6 section-news")
            
            if news_section:
                loguru.logger.info("Found news section by class")
                # Find the article link within the news section
                news_link = news_section.find("a", class_=lambda c: c and "frontpage-link" in c) or \
                            news_section.find("a", class_=lambda c: c and "medium-link" in c)
                
                if news_link:
                    results["news_headline"] = news_link.text.strip()
                    loguru.logger.info(f"News headline: {results['news_headline']}")
            else:
                # Alternate approach: look for the section header and find adjacent content
                loguru.logger.info("Looking for news section by header")
                news_headers = soup.find_all("h3", class_="frontpage-section")
                
                for header in news_headers:
                    if "News" in header.text:
                        # Look for the nearest frontpage-link after this header
                        parent = header.parent
                        if parent:
                            news_link = parent.find("a", class_=lambda c: c and ("frontpage-link" in c or "medium-link" in c))
                            if news_link:
                                results["news_headline"] = news_link.text.strip()
                                loguru.logger.info(f"News headline (header method): {results['news_headline']}")
                                break
                            
        except Exception as e:
            loguru.logger.error(f"Failed to extract news headline: {e}")
        
        # Try to extract the top sports headline
        try:
            loguru.logger.info("Attempting to extract top sports headline")
            
            # Look for the sports section header
            sports_headers = soup.find_all("h3", class_="frontpage-section")
            
            for header in sports_headers:
                if "Sports" in header.text:
                    loguru.logger.info("Found sports section header")
                    # Look within the parent container
                    parent_div = header.find_parent("div", class_=lambda c: c and "col-sm-6" in c)
                    
                    if parent_div:
                        # Find the first article summary div
                        article_summary = parent_div.find("div", class_="article-summary")
                        if article_summary:
                            sports_link = article_summary.find("a", class_=lambda c: c and ("frontpage-link" in c or "medium-link" in c))
                            if sports_link:
                                results["sports_headline"] = sports_link.text.strip()
                                loguru.logger.info(f"Sports headline: {results['sports_headline']}")
                                break
            
            # If not found by section header, try direct URL pattern
            if not results["sports_headline"]:
                loguru.logger.info("Trying alternate method for sports headline")
                sports_links = soup.find_all("a", href=lambda h: h and "/article/" in h and "sports" in h.lower())
                if sports_links and len(sports_links) > 0:
                    for link in sports_links:
                        # Check if the link has a headline-like class
                        if link.has_attr('class') and any('link' in c for c in link['class']):
                            results["sports_headline"] = link.text.strip()
                            loguru.logger.info(f"Sports headline (URL method): {results['sports_headline']}")
                            break
        
        except Exception as e:
            loguru.logger.error(f"Failed to extract sports headline: {e}")
            
        # Try to extract the top opinion headline
        try:
            loguru.logger.info("Attempting to extract top opinion headline")
            
            # Look for the opinion section header
            opinion_headers = soup.find_all("h3", class_="frontpage-section")
            
            for header in opinion_headers:
                if "Opinion" in header.text:
                    loguru.logger.info("Found opinion section header")
                    # Look within the parent container
                    parent_div = header.find_parent("div", class_=lambda c: c and "col-sm-6" in c)
                    
                    if parent_div:
                        # Find the first article summary div
                        article_summary = parent_div.find("div", class_="article-summary")
                        if article_summary:
                            opinion_link = article_summary.find("a", class_=lambda c: c and ("frontpage-link" in c or "medium-link" in c))
                            if opinion_link:
                                results["opinion_headline"] = opinion_link.text.strip()
                                loguru.logger.info(f"Opinion headline: {results['opinion_headline']}")
                                break
            
            # If not found by section header, try direct URL pattern
            if not results["opinion_headline"]:
                loguru.logger.info("Trying alternate method for opinion headline")
                opinion_links = soup.find_all("a", href=lambda h: h and "/article/" in h and "opinion" in h.lower())
                if opinion_links and len(opinion_links) > 0:
                    for link in opinion_links:
                        # Check if the link has a headline-like class
                        if link.has_attr('class') and any('link' in c for c in link['class']):
                            results["opinion_headline"] = link.text.strip()
                            loguru.logger.info(f"Opinion headline (URL method): {results['opinion_headline']}")
                            break
        
        except Exception as e:
            loguru.logger.error(f"Failed to extract opinion headline: {e}")
            
        # Check if we got at least one headline
        if all(value == "" for key, value in results.items() if key != "timestamp"):
            loguru.logger.warning("Failed to extract any headlines - site structure may have changed")
            
            # Backup extraction method - get any headline we can find
            try:
                loguru.logger.info("Attempting backup headline extraction method")
                # Try to find any headline elements
                headlines = soup.find_all("h3")
                if headlines and len(headlines) > 0:
                    results["main_headline"] = f"BACKUP METHOD: {headlines[0].text.strip()}"
                    loguru.logger.info(f"Backup headline found: {results['main_headline']}")
            except Exception as e:
                loguru.logger.error(f"Backup extraction also failed: {e}")
        
        return results
        
    except requests.exceptions.Timeout:
        loguru.logger.error("Request timed out")
        return results
    except requests.exceptions.ConnectionError:
        loguru.logger.error("Connection error")
        return results
    except Exception as e:
        loguru.logger.error(f"Unexpected error during scraping: {e}")
        return results


if __name__ == "__main__":
    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
        loguru.logger.info(f"Scraped data: {json.dumps(data_point, indent=2)}")
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None and any(value != "" for key, value in data_point.items() if key != "timestamp"):
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")
    else:
        loguru.logger.warning("No headlines found, no data saved")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    try:
        with open(dem.file_path, "r") as f:
            loguru.logger.info(f.read())
    except Exception as e:
        loguru.logger.error(f"Failed to read data file: {e}")

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")