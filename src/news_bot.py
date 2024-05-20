import re
import os
import logging
import src.variables.variables as var
from src.utils import download_image, save_to_excel
from typing import Any, Dict, List
from RPA.Browser.Selenium import Selenium, By
from datetime import datetime, timedelta




    
class NewsBot:
    def __init__(self):
       
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

        self.browser = Selenium()
       

    def search_news(self, search_phrase: str) -> None:
        """
        Perform a search on the TimesLIVE website.

        Args:
            search_phrase (str): The phrase to search for.
        """

        try:
            browser = self.browser
          
            self.browser.open_chrome_browser(url=var.NEWS_WEBSITE_URL)
            
            self.click_do_not_consent_button()
            self.close_popup()
           
            search_icon_button = var.XPATH_SEARCH_ICON
            browser.wait_until_page_contains_element(search_icon_button, timeout=20)
            browser.wait_until_element_is_visible(search_icon_button, timeout=20)
            
            browser.click_element(search_icon_button)
          
            search_input = var.XPATH_SEARCH_INPUT
            browser.wait_until_element_is_visible(search_input, timeout=20)
            browser.input_text(search_input, search_phrase)

            self.logger.info(f"Performed a search for '{search_phrase}' successfully.")
        except Exception as e:
            self.logger.error(f"Error while performing search: {e}")


    def extract_news_data(self, search_phrase: str, months_back: int, news_category: str) -> List[Dict[str, Any]]:
        """
        Extract news data based on the search phrase, number of months , and news category.

        Args:
            search_phrase (str): The phrase to search for.
            months_back (int): The number of months  to consider for news articles.
            news_category (str): The category of news to filter by.
        
        Returns:
            list: List of dictionaries containing extracted news data.
        """
        try:
            if months_back == 0:
                months_back = 1
            
            self.browser.wait_until_element_is_visible(var.XPATH_RESULT_SET, timeout=20)
            news_data = []
            results = self.browser.find_elements(var.XPATH_RESULT_ITEM)

            for result in results:
                try:
                    title_element = result.find_element(By.XPATH, var.XPATH_TITLE)
                    title = title_element.text
                    
                    url = result.get_attribute("href")

                    description_element = result.find_element(By.XPATH, var.XPATH_DESCRIPTION)
                    description = description_element.text

                    date_element = result.find_element(By.XPATH, var.XPATH_DATE)
                    date = date_element.text

                    current_time = datetime.now()
                    target_date = current_time - timedelta(days=30 * months_back)

                    if self.days_from_now(date, current_time, months_back):
                        category_elements = result.find_elements(By.XPATH, var.XPATH_CATEGORY)
                        if self.category_matches(category_elements, news_category):
                            image_element = result.find_element(By.XPATH, var.XPATH_IMAGE)
                            style_attribute = image_element.get_attribute('style')
                            image_url = self.extract_image_url_from_style(style_attribute)

                            file_name = os.path.basename(image_url) 
                            path_name = f'output/{file_name}.png'

                            download_image(image_url, path_name)

                            contains_money = self.contains_money_mention(title, description)
                            search_phrase_occurrences = self.count_search_phrase_occurrences(search_phrase, title, description)
                            
                            news_data.append({
                                "title": title,
                                "description": description,
                                "date": date,
                                "image_file_name": file_name + ".png",
                                'search_phrase_occurrences': search_phrase_occurrences,
                                "contains_money_mention": contains_money,
                            })

                except Exception as e:
                    self.logger.error(f"Error extracting data from result: {e}")
            
            save_to_excel(news_data)
            return news_data
        except Exception as e:
            self.logger.error(f"Error extracting news data: {e}")
            return []
        

    def click_do_not_consent_button(self) -> None:
            try:
                consent_button_xpath =  var.XPATH_CONSENT_BUTTON
                
                self.browser.wait_until_element_is_visible(consent_button_xpath, timeout=10)

                self.browser.click_element(consent_button_xpath)
                
                self.logger.info("Clicked on 'Do not consent' button.")
            except Exception as e:
                self.logger.error(f"Button 'Do not consent' not found or other error occurred: {e}")
                screenshot_path = self.browser.capture_page_screenshot("output/screenshot.png")
        

    def close_popup(self) -> None:

        """
        Close the popup if it is visible.

        This method waits for the popup to appear, then clicks on the close button if found.
        """
        try:
            popup_locator = var.XPATH_POPUP_LOCATOR
            close_button_locator =var.XPATH_CLOSE_POPUP

            self.browser.wait_until_element_is_visible(popup_locator, timeout=100)
            self.browser.click_element(close_button_locator)
            self.logger.info("Closed the popup successfully.")
        except AssertionError:
            self.logger.info("Popup not found or already closed.")
            pass
        except Exception as e:
            self.logger.error(f"Error while closing the popup: {e}")
            screenshot_path = self.browser.capture_page_screenshot("output/screenshot.png")
            

    def category_matches(self, category_elements: List[Any], news_category: str) -> bool:
        """
        Checks if any of the category elements in the result match the provided news category.

        Args:
            category_elements (list): List of elements representing the category elements.
            news_category (str): The category to match against.

        Returns:
            bool: True if a match is found, False if theres no match.
        """
        try:
            categories = []
            for category_element in category_elements:
                category = category_element.get_attribute("rel").strip().lower()
                categories.append(category)
            if news_category.strip().lower() in categories:
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking category match: {e}")
            return False
    

    def days_from_now(self, date_str: str, current_time: datetime, months_back: int) -> bool:
        """
        Check if the given date is within the specified number of months back.

        Args:
            date_str (str): String representation of the date.
            current_time (datetime): Current datetime object.
            months_back (int): Number of months to check against.

        Returns:
            bool: True if the date is within the specified timeframe, False otherwise.
        """
        try:
            match = re.search(r'(\d+)\s+(\w+)\s+ago', date_str)
            if match:
                number, unit = int(match.group(1)), match.group(2)
                if unit.startswith('hour'):
                    target_date = current_time - timedelta(hours=number)
                elif unit.startswith('day'):
                    target_date = current_time - timedelta(days=number)
                elif unit.startswith('week'):
                    target_date = current_time - timedelta(weeks=number)
                elif unit.startswith('month'):
                    target_date = current_time - timedelta(days=30 * number)
                elif unit.startswith('year'):
                    target_date = current_time - timedelta(days=365 * number)
                return (current_time - target_date).days <= months_back * 30
            return False
        except Exception as e:
            self.logger.error(f"Error checking days from now: {e}")
            return False
    

    def extract_image_url_from_style(self, style_attribute):
        """
        Extract the image URL from the style attribute.

        Args:
            style_attribute (str): Style attribute containing the image URL.

        Returns:
            str: Extracted image URL if found, otherwise None.
        """
        try:
            if style_attribute:
                matches = re.search(r"url\(\"?([^\"?]+)\"?\)", style_attribute)
                if matches:
                    return matches.group(1)
            return None
        except Exception as e:
            self.logger.error(f"Error extracting image URL from style attribute: {e}")
            return None


    def contains_money_mention(self, title: str, description: str) -> bool:
        """
        Check if the title or description contains any mention of money.

        Args:
            title (str): Title of the news article.
            description (str): Description of the news article.

        Returns:
            bool: True if either the title or description contains money, False if they dont.
        """
        try:
            money_pattern = r'\$[\d,.]+|\d+\s*(?:dollars|USD)\b|R[\d,.]+|\d+\s*rands\b'

            title_contains_money = re.search(money_pattern, title, re.IGNORECASE) is not None

            description_contains_money = re.search(money_pattern, description, re.IGNORECASE) is not None

            return title_contains_money or description_contains_money
        except Exception as e:
            self.logger.error(f"Error checking mention of money : {e}")
            return False
        
    
    def count_search_phrase_occurrences(self, search_phrase: str, title: str, description: str) -> int:
        """
        Count occurrences of the search phrase in the title and description.

        Args:
            search_phrase (str): The phrase to search for.
            title (str): Title of the news article.
            description (str): Description of the news article.

        Returns:
            int: Total count of occurrences of the search phrase.
        """
        try:
            search_phrase_lower = search_phrase.lower()
            title_lower = title.lower()
            description_lower = description.lower()

            title_occurrences = title_lower.count(search_phrase_lower)
            description_occurrences = description_lower.count(search_phrase_lower)
            
            total_occurrences = title_occurrences + description_occurrences
            return total_occurrences
        except Exception as e:
            self.logger.error(f"Error counting search phrase occurrences: {e}")
            return 0
