import logging
from robocorp.tasks import task
from robocorp import workitems
from RPA.Robocorp.WorkItems import WorkItems
from src.news_bot import NewsBot


logging.basicConfig(level=logging.INFO)
@task
def minimal_task():
    bot = NewsBot()
  
    try:
        for item in workitems.inputs:
            search_phrase = item.payload["search_phrase"]
            num_months = item.payload["num_months"]
            news_category= item.payload["news_category"]

            bot.search_news(search_phrase)
            bot.extract_news_data(search_phrase,num_months,news_category)

    except Exception as e:
        logging.error(f"An error occurred: {e}")