from DataScaper.Utils.Parameter import class2code, flight_type2code, city2airport

DOMAIN = 'https://vn.trip.com'
SUB_PAGE = 'flight'


def url_assembler(dcity, acity, ddate, rdate, flight_type, class_type):
    """Assemble the url to get the search web page"""
    class_code = class2code[class_type]
    flight_type = flight_type2code[flight_type]
    dcity_code = city2airport[dcity].lower()
    acity_code = city2airport[acity].lower()
    url = f'{DOMAIN}/{SUB_PAGE}/{dcity}-to-{acity}/tickets-{dcity_code}-{acity_code}?dcity={dcity_code}&acity={acity_code}&ddate={ddate}&rdate={rdate}&flighttype={flight_type}&class={class_code}&lowpricesource=searchform&quantity=1&searchboxarg=t&nonstoponly=off&locale=vi-VN&curr=VND'
    return url


def url_disassembler(url):
    """Disassemble the url to get the search parameters"""
    parts = url.split('/')
    dcity = parts[4].split('-')[0]
    acity = parts[4].split('-')[2]
    queries = parts[5].split('?')
    ddate = queries[1].split('&')[1].split('=')[1]
    rdate = queries[1].split('&')[2].split('=')[1]
    flight_type = queries[1].split('&')[3].split('=')[1]
    class_type = queries[1].split('&')[4].split('=')[1]
    return dcity, acity, ddate, rdate, flight_type, class_type


def parse_price(price):
    """XXX.XXX.XXX.XXX₫ -> XXXXXXXXX"""
    return int(price.replace('.', '').replace('₫', ''))


def fcode_parse(data):
    parts = data.split('^')
    parts = parts[0].split(',')
    fcodes = []
    for part in parts:
        fcodes.append(part.split('-')[0])
    return fcodes


def flight_parse(flight):
    """Parse the content of a web element to get the flight info. Return format: {brand, dtime, flytime, atime, price}"""
    brand = flight.xpath("//div[starts-with(@class, 'flights-name')]")[0].text
    dtime = flight.xpath("//div[contains(@class, 'is-dep_')]")[0].find_class("time")[0].text
    atime = flight.xpath("//div[contains(@class, 'is-arr_')]")[0].find_class("time")[0].text
    flytime = flight.xpath("//div[starts-with(@class, 'flight-info-duration')]")[0].text
    rprice = flight.find_class('o-price-flight')[0].text
    price = parse_price(rprice)
    fcode = fcode_parse(flight.find_class('select-area')[0].get('data-shoppingid'))
    return {'brand': brand, 'dtime': dtime, 'flytime': flytime, 'atime': atime, 'price': price, 'fcode': fcode}


def flights_parse(root):
    flights = root.find_class('J_FlightItem')
    return flights
