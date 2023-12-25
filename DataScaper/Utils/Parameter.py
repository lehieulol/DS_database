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

required = {'selenium', 'webdriver-manager', 'pygithub', 'schedule', 'lxml'}

LOG_FILE = 'flight_crawler.log'
