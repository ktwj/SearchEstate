from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import select
from selenium.webdriver.support.select import Select
from time import sleep
import logging, random
from pysrc import celery

@celery.task
def ope(station, min, times, rent, walktime, sites):
    options = webdriver.ChromeOptions()
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        ]
    
    USER_AGENT = user_agents[random.randrange(0, len(user_agents), 1)]
    options.add_argument('--headless')                 # headlessモードを使用する
    options.add_argument('--disable-gpu')              # headlessモードで暫定的に必要なフラグ(そのうち不要になる)
    options.add_argument('--disable-extensions')       # すべての拡張機能を無効にする。ユーザースクリプトも無効にする
    #options.add_argument('--proxy-server="socks5://127.0.0.1:port"') # Proxy経由ではなく直接接続する
    #options.add_argument('--proxy-bypass-list=*')      # すべてのホスト名
    options.add_argument('--start-maximized')          # 起動時にウィンドウを最大化する
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.use_chromium = True
    options.add_argument(f'--user-agent={USER_AGENT}')

    l = []
    logger = logging.getLogger()

    # sites に True が入っていたらブラウザ起動
    if True in sites:
        # driver 起動
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        if sites[0]:
            try:
                #raise ValueError('error')
                
                # suumo　接続    
                init_url = 'http://suumo.jp/chintai/kanto'
                driver.get(init_url)
                sleep(10)

                # 賃貸検索へ
                search_by_time = driver.find_element(By.CLASS_NAME, 'btn_topsearch01')
                search_by_time.click()

                sleep(10)

                # 駅名入力
                select_station = driver.find_element(By.CLASS_NAME, 'js-ekiTextBox')
                select_station.send_keys(station)
                sleep(3)

                # 上記駅までの所要時間入力
                select_time = driver.find_elements(By.CLASS_NAME, 'js-removeEnsen')[0]
                select1 = Select(select_time)
                select1.select_by_value(min)
                sleep(3)

                # 乗り換え回数入力
                select_times = driver.find_elements(By.CLASS_NAME, 'js-removeEnsen')[1]
                select2 = Select(select_times)
                select2.select_by_value(times)
                sleep(3)

                # 賃料・管理費・共益費の合計入力
                select_limit = driver.find_element(By.CLASS_NAME, 'selectunit').find_elements(By.TAG_NAME, 'select')[1]
                select3 = Select(select_limit)
                select3.select_by_value(rent)
                sleep(3)

                # 管理費共益費込みボタンクリック
                select_pay = driver.find_element(By.ID, 'co0')
                select_pay.click()

                # 最寄り駅徒歩所要時間上限クリック
                time2walk = driver.find_element(By.XPATH, "//input[@name='et' and @value='"+walktime+"']")
                time2walk.click()
                sleep(3)

                # 検索ボタン クリック
                submit = driver.find_element(By.CLASS_NAME, 'js-searchBtn')
                submit.click()

                flg = False

                for i in range(3):
                    listss = driver.find_elements(By.CLASS_NAME, 'l-cassetteitem')
                    for lists in listss:
                        list = lists.find_elements(By.CLASS_NAME, 'cassetteitem')
                        for item in list:
                            # 物件名取得
                            title = item.find_element(By.CLASS_NAME, 'cassetteitem_content-title').text

                            # 最寄り駅取得
                            near_stations = item.find_elements(By.CLASS_NAME, 'cassetteitem_detail-text')
                            stations_l = []
                            if near_stations is not None:
                                for near_station in near_stations:
                                    stations_l.append(near_station.text)

                            # アドレスを複数取得、なければパス
                            urls = item.find_elements(By.CLASS_NAME, 'js-cassette_link_href')
                            urls_l = []
                            if urls is not None:
                                for url in urls:
                                    urls_l.append(url.get_attribute('href'))

                            # 賃料と手数料を取得
                            rents = item.find_elements(By.CLASS_NAME, 'cassetteitem_price--rent')
                            fees = item.find_elements(By.CLASS_NAME, 'cassetteitem_price--administration')
                            prices = []

                            # 賃料と手数料を1つの文字列に統合
                            if rents is not None:
                                for i in range(len(rents)):
                                    if rents[i].text is None:rents[i].text = '-'
                                    if fees[i].text is None:fees[i].text = '-'
                                    price = rents[i].text +' + ' +fees[i].text
                                    prices.append(price)

                            # 目的駅への所要時間・乗り換え回数
                            # transfers = item.find_elements(By.XPATH, '//ul[@class="cassetteitem_transfer-list"]/li')
                            transfers = item.find_element(By.CLASS_NAME, 'cassetteitem_transfer-list').find_elements(By.TAG_NAME, 'li')
                            transfers_l = []
                            if transfers is not None:
                                for transfer in transfers:
                                    transfers_l.append(transfer.text)

                            # itemリストに入れ、lリストに入れる
                            item = []
                            item.append(title)
                            item.append(stations_l)
                            item.append(urls_l)
                            item.append(prices)
                            item.append(transfers_l)
                            l.append(item)

                            if len(l)>=100:
                                flg = True
                                break
                        if flg:break
                    if flg:break
                            
                    next = driver.find_elements(By.XPATH, '//div/p[@class="pagination-parts"]/a')
                    sleep(5)

                    if len(next) == 0:
                        break
                    else:
                        next_url = next[0].get_attribute('href')
                        driver.get(next_url)

            except Exception as e:
                logger.exception('Exception 2: ' + str(e))

        if sites[1]:
            try:
                next_url = 'https://www.athome.co.jp/chintai/commute_time/'
                driver.get(next_url)
                sleep(15)

                # 目的駅指定
                select_station = driver.find_element(By.ID, 'inputStation')
                select_station.send_keys(station)
                sleep(5)

                # 所要時間指定
                select_time = driver.find_element(By.NAME, 'VEKI_TIME1')
                select1 = Select(select_time)
                select1.select_by_value(min)
                sleep(5)

                # 乗り換え回数指定
                if times == '-1':pass
                else:
                    select_times = driver.find_element(By.NAME, 'VEKI_TRANS1')
                    select2 = Select(select_times)
                    select2.select_by_value(times)
                sleep(5)

                # 賃料指定
                rdict = {
                    '3.0':'kc101', '3.5':'kc102', '4.0':'kc103', '4.5':'kc104', '5.0':'kc105', '5.5':'kc106', '6.0':'kc107', '6.5':'kc108',
                    '7.0':'kc109', '7.5':'kc110', '8.0':'kc111', '8.5':'kc112', '9.0':'kc113', '9.5':'kc114', '10.0':'kc115','11.0':'kc117',
                    '12.0':'kc119','13.0':'kc121','14.0':'kc123','15.0':'kc125','16.0':'kc127','17.0':'kc129','18.0':'kc131',
                    '19.0':'kc133','20.0':'kc134','30.0':'kc135','50.0':'kc136','100.0':'kc137'
                }
                e = ''
                for k,v in rdict.items():
                    e = e + f'"{v}" if rent=="{k}" else '
                e = e + ' rdict["100.0"]'
                r = eval(e)

                select_limit = driver.find_element(By.NAME, 'PRICETO')
                select3 = Select(select_limit)
                select3.select_by_value(r)
                sleep(3)

                # 管理費共益費込みボタンクリック
                select_pay = driver.find_element(By.NAME, 'PRICEOPT[]')
                select_pay.click()
                sleep(3)

                # 駅までの所要時間指定
                if walktime=='9999999':pass
                else:
                    vdict = {'1':'ke102','5':'ke003','7':'ke101','10':'ke004','15':'ke005','20':'ke006'}
                    e = ''
                    for k,v in vdict.items():
                        e = e + f'"{v}" if walktime=="{k}" else '
                    e = e + "ke001"
                    v = eval(e)

                    time2walk = driver.find_element(By.XPATH, f'//input[@name="EKITOHO" and @value="{v}"]')
                    time2walk.click()
                sleep(5)

                driver.find_element(By.CLASS_NAME, 'ir-bt_view_result').click()

                sleep(10)
                elem = driver.find_elements(By.ID, 'build_display')
                if len(elem) == 0:
                    pass
                else:
                    loc = elem[0].location
                    x,y = loc['x']+10, loc['y']+10
                    webdriver.ActionChains(driver).move_by_offset(x,y).click().perform()

                lists = driver.find_elements(By.CLASS_NAME, 'p-property--building')
                for item in lists:
                    # 物件名
                    title = item.find_element(By.CLASS_NAME, 'p-property__title--building').text

                    # 最寄り駅取得
                    near_station = item.find_elements(By.CLASS_NAME, "p-property__information-hint")[1]
                    near_station = near_station.find_element(By.TAG_NAME, 'dd').text
                    stations_l = []
                    stations_l.append(near_station)

                    # アドレスを複数取得
                    urls = item.find_elements(By.CLASS_NAME, 'p-property__room-more-inner')
                    urls_l = []
                    for url in urls:
                        urls_l.append(url.get_attribute('href'))
                    
                    # 賃料手数料を取得
                    rents = item.find_elements(By.CLASS_NAME, 'p-property__information-rent')
                    fees = item.find_elements(By.CLASS_NAME, 'p-property__information-price')
                    prices = []

                    # 賃料と手数料を1つの文字列に統合
                    if rents is not None:
                        for rent, fee in zip(rents, fees):
                            fee_text = fee.find_element(By.TAG_NAME, 'span').text
                            if rent.text is None or rent.text == '':rent.text = '-'
                            if fee_text  is None or fee_text  == '':fee_text = '-'
                            price = rent.text.replace(',', '.') +'万円 + ' +fee_text.replace(',', '.')
                            prices.append(price)
                    print(prices)

                    # 目的駅への所要時間、乗り換え回数
                    transfers_l = []
                    transfer = item.find_element(By.CLASS_NAME, 'p-property__time-station').text
                    transfers_l.append(transfer)

                    # itemリストに入れる、lリストに入れる
                    item = []
                    item.append(title)
                    item.append(stations_l)
                    item.append(urls_l)
                    item.append(prices)
                    item.append(transfers_l)
                    l.append(item)
            
            except Exception as e:
                logger.exception('Exception 2: ' + str(e))
                return l

        if sites[2]:
            try:
                next_url = 'https://www.homes.co.jp/chintai/'
                sleep(10)
                driver.get(next_url)

                driver.find_element(By.ID, 'prg-transitMenuButton').click()
                driver.find_element(By.ID, 'prg-transit_eki_item1').send_keys(station)
                sleep(3)

                if min == '-1':pass
                else:
                    select_time = driver.find_element(By.NAME, 'cond[commute_time][0]')
                    select1 = Select(select_time)
                    select1.select_by_value(min)
                sleep(3)

                select_times = driver.find_element(By.NAME, 'cond[commute_transfer_count][0]')
                select2 = Select(select_times)
                select2.select_by_value(times)
                sleep(15)

                search_btn = driver.find_elements(By.CLASS_NAME, 'submit')
                sleep(3)
                if len(search_btn) == 0:
                    pass
                else:
                    loc = search_btn[0].location
                    x,y = loc['x'] +1, loc['y'] +1
                    webdriver.ActionChains(driver).move_by_offset(x,y).click().perform()

                    sleep(10)

                    # 家賃上限指定
                    rent_elem = driver.find_element(By.ID, 'cond_monthmoneyroomh')
                    select3 = Select(rent_elem)
                    rent = rent if float(rent)<10 else rent[-2:]
                    select3.select_by_value(rent)
                    sleep(10)
                
                    # 管理費共益費込み指定
                    driver.find_element(By.ID, 'cond_kanrihi').click()
                    sleep(10)

                    # 徒歩分数指定
                    walktime_elem = driver.find_element(By.ID, 'cond_walkminutesh')
                    select4 = Select(walktime_elem)
                    select4.select_by_value(walktime)
                    sleep(10)

                    # 物件指定
                    lists = driver.find_elements(By.CLASS_NAME, 'mod-mergeBuilding--rent--photo')

                    for item in lists:
                        # 物件名
                        title = item.find_element(By.CLASS_NAME, 'bukkenName').text

                        # アドレス取得
                        urls_l = []
                        urls = item.find_elements[By.XPATH, '//td[@class="detail"]/a']
                        for url in urls:
                            urls_l.append(url.get_attribute('href'))

                        # 所要時間取得
                        transfers_l = []
                        transfer = item.find_element(By.CLASS_NAME, 'station').text +'まで' +item.find_element(By.CLASS_NAME, 'time').text +'（' +item.find_element(By.XPATH, '//span[@class="transfer"]/a').text +'）'
                        transfers_l.append(transfer)

                        # 最寄り駅取得
                        stations_l = []
                        near_stations = item.find_elements(By.CLASS_NAME, 'prg-stationText')
                        stations = [station.text for station in near_stations]
                        stations_l.append(stations)

                        # 賃料手数料を取得
                        rents = item.find_elements(By.CLASS_NAME, 'price')
                        prices = []
                        for rent in rents:
                            prices.append(rent.text)

                        item = []
                        item.append(title)
                        item.append(stations_l)
                        item.append(urls_l)
                        item.append(prices)
                        item.append(transfers_l)
                        l.append(item)
            except:
                return l

    return l

"""
station = '茅場町'
min = '10'
times = '0'
rent = '6.0'
walktime = '5'
sites = [False, False, True]

l = ope(station, min, times, rent, walktime, sites)

for n in l:
    print(n)
"""