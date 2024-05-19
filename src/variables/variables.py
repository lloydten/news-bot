from pathlib import Path
from datetime import datetime


current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
ROOT_DIR = Path(__file__).resolve().parent

NEWS_WEBSITE_URL = "https://www.timeslive.co.za/"

OUTPUT_DIRECTORY = ROOT_DIR / "output"
EXCEL_FILE_PATH = f"{OUTPUT_DIRECTORY}/news_data_{current_time}.xlsx"

XPATH_CONSENT_BUTTON = "//*[contains(text(), 'Do not consent')]"
XPATH_POPUP_LOCATOR = "//div[@id='register-popup']"
XPATH_CLOSE_POPUP = "//a[@id='register-popup-modal-close']"
XPATH_REGISTER_POPUP = "//div[@id='register-popup']"
XPATH_SEARCH_ICON = "id:nav-search"
XPATH_SEARCH_INPUT = "//input[@placeholder='Search TimesLIVE']"
XPATH_RESULT_SET = "//div[@class='result-set']"
XPATH_RESULT_ITEM = "//div[@class='result-set']/a[@class='result']"
XPATH_TITLE = ".//h2"
XPATH_DESCRIPTION = ".//p"
XPATH_DATE = ".//div[@class='date-stamp']"
XPATH_CATEGORY = ".//div[@class='section']//span[@rel]"
XPATH_IMAGE = ".//span[@class='image']"