from DataScaper.Utils.Driver import get_driver
from DataScaper.Utils.Parameter import required, LOG_FILE, SCROLL_SCRIPT, class2code, city2airport
from DataScaper.Utils.Setup import setup

setup(required)

from DataScaper.Parser.TripVn import url_disassembler, url_assembler, flight_parse
from DataScaper.Utils.Datetime import date_assembler
from DataScaper.Utils.Email import send_mail
from DataScaper.Utils.Github import github_login, github_save

import time
import schedule
import datetime

import logging
import multiprocessing

import selenium
from lxml import html

logging.basicConfig(level=logging.INFO, filemode='w', filename=LOG_FILE)


def save_info(info, filename):
    with open(filename, 'a') as f:
        f.write(info + '\n')


def send_query(url, driver):
    logger = logging.getLogger("FlightInfoGetter")
    try:
        driver.get(url)
        try:
            driver.execute_async_script(SCROLL_SCRIPT)
        except:
            pass

        source = driver.page_source
        root = html.document_fromstring(source)
        flights = root.find_class('J_FlightItem')
        if len(flights) == 0:
            queries = url_disassembler(url)
            logger.warning(f"No flights with query: {queries}.")
        return flights
    except selenium.common.exceptions.StaleElementReferenceException:
        logger.error(
            f"StaleElementReferenceException when getting flights at url: {url} and queries {queries}. Retrying...")
        return send_query(url, driver)


def scrape():
    repo = github_login()
    logger = logging.getLogger("MainController")
    OUTPUT_FILE = f'flight_info {datetime.date.today().isoformat()}.txt'
    flight_type = 'oneway'
    return_date_distance = 2
    start_date = datetime.date.today()
    end_date = datetime.date.today() + datetime.timedelta(days=10)
    driver = get_driver()
    for date in range((end_date - start_date).days + 1):
        curr_date = start_date + datetime.timedelta(days=date)
        departure_date = date_assembler(curr_date.year, curr_date.month, curr_date.day)
        return_date_obj = curr_date + datetime.timedelta(days=return_date_distance)
        return_date = date_assembler(return_date_obj.year, return_date_obj.month, return_date_obj.day)
        for class_type in class2code.keys():
            for dcity in city2airport.keys():
                for acity in city2airport.keys():
                    if dcity == acity:
                        continue
                    logger.info(
                        f"Crawling {dcity} -> {acity} on {curr_date} with {class_type} class, crawl date: {datetime.date.today().isoformat()}")
                    url = url_assembler(dcity, acity, departure_date, return_date, flight_type, class_type)
                    print(url)
                    flights = send_query(url, driver)
                    for flight in flights:
                        try:
                            flight_info = flight_parse(flight)
                            flight_info["crawl_date"] = datetime.date.today().isoformat()
                            flight_info["dcity"] = dcity
                            flight_info["acity"] = acity
                            flight_info["flight_type"] = flight_type
                            flight_info["class_type"] = class_type
                            flight_info["ddate"] = curr_date.isoformat()
                            save_info(str(flight_info), OUTPUT_FILE)
                        except Exception as e:
                            send_mail(
                                f'Exception is occurred during {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} while crawling',
                                str(e))

            github_save(repo, OUTPUT_FILE)


def start_new():
    try:
        t1 = multiprocessing.Process(target=scrape)
        t1.start()
    except Exception as e:
        send_mail(
            f'Exception is occurred during {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} while crawling',
            str(e))


if __name__ == '__main__':
    send_mail(f'Crawling starting {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}', 'Email ready check')
    schedule.every().day.at("01:00").do(start_new)
    while True:
        schedule.run_pending()
        time.sleep(60)
