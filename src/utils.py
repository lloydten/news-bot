from typing import Any, Dict, List, Optional
import requests
import logging
import pandas as pd
from datetime import datetime
import src.variables.variables as var
from RPA.Browser.Selenium import Selenium
logging.basicConfig(level=logging.INFO)

def download_image(image_url: str, save_path: str) -> bool:
    """
    Download an image from a URL and save it to a specified path.

    Args:
        image_url (str): The URL of the image to download.
        save_path (str): The file path where the image will be saved.

    Returns:
        bool: True if the image was downloaded and saved successfully, False otherwise.
    """
   
    try:
        browser = Selenium()
        browser.open_available_browser(image_url)
        
        image_content = browser.get_source()

        with open(save_path, 'wb') as file:
            file.write(image_content.encode('utf-8'))

        logging.info(f"Image downloaded successfully: {save_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to download or save image: {e}")
        return False
    # finally:
    #     browser.close_browser()
    
def save_to_excel(data: List[Dict[str, Any]]) -> Optional[str]:

    """
    Save data to an Excel file.

    Args:
        data (list): List of dictionaries containing data to be saved.

    Returns:
        str or None: File path of the saved Excel file if successful, None otherwise.
    """
    try:
        news_df = pd.DataFrame(data)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        excel_file_path = f"output/news_data_{current_time}.xlsx"

        news_df.to_excel(excel_file_path, index=False)

        logging.info(f"Data saved to Excel successfully at {excel_file_path}")
        return excel_file_path
    except Exception as e:
        logging.error(f"Failed to save data to Excel. Error: {e}")
        return None