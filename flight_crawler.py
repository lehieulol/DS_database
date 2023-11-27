def setup(required):
    import subprocess
    import sys
    import pkg_resources
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        # implement pip as a subprocess:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
    else:  # Update all required packages
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', *required])


required = {'selenium', 'webdriver-manager', 'pygithub'}
setup(required)

import logging

logging.basicConfig(level=logging.INFO, filemode='w', filename='flight_crawler.log')

from webdriver_manager.chrome import ChromeDriverManager
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import selenium

from github import Github
from github import Auth

DOMAIN = 'https://vn.trip.com'
SUB_PAGE = 'flight'
city2airport = {'ho-chi-minh-city': 'SGN', 'da-nang': 'DAD', 'hanoi': 'han', 'phu-quoc-island': 'PQC',
                'nha-trang': 'CXR', 'hue': 'HUI', 'vinh': 'VII', 'haiphong': 'HPH', 'dong-hoi': 'VDH', 'chu-lai': 'VCL',
                'pleiku': 'PXU', 'buon-ma-thuot': 'BMV', 'rach-gia': 'VKG', 'ca-mau': 'CAH', 'con-dao-island': 'VCS',
                'Da-lat': 'DLI', 'Can-tho': 'VCA', 'dien-bien-phu': 'DIN'}

flight_type2code = {'oneway': 'ow', 'roundtrip': 'rt'}
class2code = {'economy': 'ys', 'business': 'cf'}

SCROLL_SCRIPT = """
        count = 400;
        let callback = arguments[arguments.length - 1];
        t = setTimeout(function scrolldown(){
            console.log(count, t);
            window.scrollTo(0, count);
            if(count < (document.body.scrollHeight || document.documentElement.scrollHeight)){
              count+= 400;
              t = setTimeout(scrolldown, 300);
            }else{
              callback((document.body.scrollHeight || document.documentElement.scrollHeight));
            }
        }, 1000);"""


def url_assembler(dcity, acity, ddate, rdate, flight_type, class_type):
    '''Assemble the url to get the search web page'''
    class_code = class2code[class_type]
    flight_type = flight_type2code[flight_type]
    dcity_code = city2airport[dcity].lower()
    acity_code = city2airport[acity].lower()
    url = f'{DOMAIN}/{SUB_PAGE}/{dcity}-to-{acity}/tickets-{dcity_code}-{acity_code}?dcity={dcity_code}&acity={acity_code}&ddate={ddate}&rdate={rdate}&flighttype={flight_type}&class={class_code}&lowpricesource=searchform&quantity=1&searchboxarg=t&nonstoponly=off&locale=vi-VN&curr=VND'
    return url


def date_assembler(year, month, day):
    '''Assemble the date to the format: YYYY-MM-DD'''
    if month < 10:
        month = f'0{month}'
    if day < 10:
        day = f'0{day}'
    return f'{year}-{month}-{day}'


def url_disassembler(url):
    '''Disassemble the url to get the search parameters'''
    parts = url.split('/')
    dcity = parts[4].split('-')[0]
    acity = parts[4].split('-')[2]
    queries = parts[5].split('?')
    ddate = queries[1].split('&')[1].split('=')[1]
    rdate = queries[1].split('&')[2].split('=')[1]
    flight_type = queries[1].split('&')[3].split('=')[1]
    class_type = queries[1].split('&')[4].split('=')[1]
    return dcity, acity, ddate, rdate, flight_type, class_type


def get_flights(url, driver):
    logger = logging.getLogger("FlightInfoGetter")
    try:
        driver.get(url)
        driver.execute_async_script(SCROLL_SCRIPT)
        flights = driver.find_elements(By.CLASS_NAME, 'J_FlightItem')
        if len(flights) == 0:
            queries = url_disassembler(url)
            logger.warning(f"No flights with query: {queries}.")
        return flights
    except selenium.common.exceptions.StaleElementReferenceException:
        logger.error(
            f"StaleElementReferenceException when getting flights at url: {url} and queries {queries}. Retrying...")
        return get_flights(url, driver)


def parse_price(price):
    '''XXX.XXX.XXX.XXX₫ -> XXXXXXXXX'''
    return int(price.replace('.', '').replace('₫', ''))


def fight_parse(flight):
    '''Parse the content of a web element to get the flight info. Return format: {brand, dtime, flytime, atime, price}'''
    brand = flight.find_element(By.CLASS_NAME, 'flights-name_25v').text
    dtime = flight.find_element(By.CLASS_NAME, 'is-dep_2l7').find_element(By.CLASS_NAME, 'time').text
    atime = flight.find_element(By.CLASS_NAME, 'is-arr_2lp').find_element(By.CLASS_NAME, 'time').text
    flytime = flight.find_element(By.CLASS_NAME, 'flight-info-duration_2po').text
    rprice = flight.find_element(By.CLASS_NAME, 'o-price-flight').text
    price = parse_price(rprice)
    return {'brand': brand, 'dtime': dtime, 'flytime': flytime, 'atime': atime, 'price': price}


def save_info(info, filename):
    with open(filename, 'a') as f:
        f.write(info + '\n')


def github_login():
    auth = Auth.Token("redacted")
    g = Github(auth=auth)

    repo = g.get_user().get_repo('DS_database')
    return repo


def github_save(repo, file_name):
    with open(f'./{file_name}', 'r') as file:
        content = file.read()

    git_file = f'DS_database/{file_name}'
    try:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "database update", content, contents.sha, branch="master")
    except Exception:
        repo.create_file(git_file, "database create", content, branch="master")


def main():
    repo = github_login()
    logger = logging.getLogger("MainController")
    OUTPUT_FILE = 'flight_info.txt'
    flight_type = 'oneway'
    return_date_distance = 2
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2021, 1, 2)
    for class_type in class2code.keys():
        for dcity in city2airport.keys():
            for acity in city2airport.keys():
                if dcity == acity:
                    continue
                for date in range((end_date - start_date).days + 1):
                    curr_date = start_date + datetime.timedelta(days=date)
                    logger.info(f"Crawling {dcity} -> {acity} on {curr_date} with {class_type} class")
                    departure_date = date_assembler(curr_date.year, curr_date.month, curr_date.day)
                    return_date_obj = curr_date + datetime.timedelta(days=return_date_distance)
                    return_date = date_assembler(return_date_obj.year, return_date_obj.month, return_date_obj.day)
                    url = url_assembler(dcity, acity, departure_date, return_date, flight_type, class_type)
                    flights = get_flights(url, driver)
                    for flight in flights:
                        flight_info = fight_parse(flight)
                        flight_info["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
                        flight_info["dcity"] = dcity
                        flight_info["acity"] = acity
                        flight_info["flight_type"] = flight_type
                        flight_info["class_type"] = class_type
                        save_info(str(flight_info), OUTPUT_FILE)
                github_save(repo, OUTPUT_FILE)
                github_save(repo, "flight_crawler.log")


if __name__ == "__main__":
    main()
