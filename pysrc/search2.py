from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from time import sleep
import logging, random, re, datetime
from bs4 import BeautifulSoup
import pandas as pd

def line_and_station_and_time(l):
    # '〇〇線/××駅 歩5分' から 'xx駅 歩5分'を取り出し、['xx駅',5]にして　それぞれをreturn
    if l: return l[:l.find('/')], l[l.find('/')+1:].split(' ')[0], int(re.sub(r"\D",'' , l[l.find('/')+1:].split(' ')[1]))
    else: return None, None, None

def check_mann(p):
    # 文字列に円が含まれている
    if '円' in p:
        # 文字列に万が含まれていたら、数値をfloatで取り出し10000倍
        if '万' in p: return float(re.sub(r"[^\d.]",'',p)) * 10000
        # 文字列に千が含まれていたら、数値をfloatで取り出し1000倍
        elif '千' in p: return float(re.sub(r"[^\d.]",'',p)) * 1000
        # 文字列に数詞がなければ、数値をfloatで取り出す
        else: return float(re.sub(r"[^\d.]",'',p))
    # 文字列に円がなければ（'-' のみなど）、0を返す
    else: return 0

def getter():
    options = webdriver.ChromeOptions()
    user_agents = [
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36'
        ]

    USER_AGENT = user_agents[random.randrange(0, len(user_agents), 1)]
    options.add_argument('--headless')                 # headlessモードを使用する
    options.add_argument('--disable-gpu')              # headlessモードで暫定的に必要なフラグ(そのうち不要になる)
    options.add_argument('--disable-extensions')       # すべての拡張機能を無効にする。ユーザースクリプトも無効にする
    options.add_argument('--no-sandbox')               # サンドボックス使用しない
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--proxy-server="socks5://127.0.0.1:port"') # Proxy経由ではなく直接接続する
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--proxy-bypass-list=*')      # すべてのホスト名
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.use_chromium = True
    options.add_argument(f'--user-agent={USER_AGENT}')

    search_list = []

    # driver 起動
    driver = webdriver.Chrome(options=options)
    try:
        driver.implicitly_wait(10)

        tokyo = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&cb=0.0&ct=8.0&mb=0&mt=9999999&et=10&cn=15&co=1&kz=1&kz=2&kz=4&tc=0400301&tc=0400101&tc=0400501&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=%26%23039%3b&sngz=&po1=25&pc=50'
        # kanagawa = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&kz=1&kz=2&kz=4&shkr1=03&shkr2=03&shkr3=03&shkr4=03&ta=14&cb=0.0&ct=8.0&co=1&et=10&mb=0&mt=9999999&cn=15&tc=0400301&tc=0400101&tc=0400501&fw2=%27'

        global bukken_num
        bukken_num = 0

        # listsはsuumoのページ numは現在のページ数 lastは最後のページ
        def get(lists,num,last):
            global bukken_num
            for list in lists:
                items = list.find_all('div', class_='cassetteitem')
                for item in items:
                    title = item.find('div', class_='cassetteitem_content-title').text
                    address = item.find('li', class_='cassetteitem_detail-col1').text

                    stations_l = [s.get_text() for s in item.select('div.cassetteitem_detail-text')]
                    line1, station1, time1 = line_and_station_and_time(stations_l[0])
                    line2, station2, time2 = line_and_station_and_time(stations_l[1])
                    line3, station3, time3 = line_and_station_and_time(stations_l[2])

                    parts = item.find_all('tr', class_='js-cassette_link')
                    for part in parts:
                        prices = [p.get_text() for p in part.select('span.cassetteitem_price')]

                        rent  = check_mann(prices[0])
                        fee   = check_mann(prices[1])
                        dep   = check_mann(prices[2])
                        key   = check_mann(prices[3])
                        price = rent + fee

                        room_type = part.find('span', class_='cassetteitem_madori').text
                        room_size = float(re.sub(r"[^\d.]", '' ,part.find('span', class_='cassetteitem_menseki').text[:-1]))

                        url = 'https://suumo.jp' +part.find('a',class_='js-cassette_link_href').get('href')

                        search_item = [bukken_num, title, address, line1,station1,time1, line2,station2,time2, line3,station3,time3, price, rent, fee, dep, key, room_type, room_size, url]
                        search_list.append(search_item)
                    bukken_num += 1
            # もし現在のページが最後のページなら終了
            if num==last:return
            else:
                num += 1
                driver.get(f'{tokyo}&page={num}')
                html = driver.page_source.encode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                lists = soup.find_all('ul', class_='l-cassetteitem')
                sleep(10)
                get(lists,num,last)

        driver.get(tokyo)
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        lists = soup.find_all('ul', class_='l-cassetteitem')
        pg = driver.find_elements(By.XPATH, '//ol[@class="pagination-parts"]/li')
        if len(pg) == 0:pass
        else:
            last = int(pg[-1].text)
        num = 1
        last = 2
        get(lists, num, last)
        driver.close()
        sl = pd.DataFrame(search_list, columns=['bukken_num', 'title', 'address', 'line1','station1','time1','line2','station2','time2','line3','station3','time3','price', 'rent', 'fee', 'deposit', 'key', 'room_type','room_size', 'url'], )
        
        return sl
    except Exception as e:
        print(e)
        return None