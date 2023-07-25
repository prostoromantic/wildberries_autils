import datetime

from loguru import logger
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from random import choice, randint
import zipfile
import configparser
import pickle
from wb_applications.models import Account, Ransoms, Address


def get_settings(key, value):
    config = configparser.ConfigParser()
    config.read('settings.ini', encoding='utf-8')
    return config.get(key, value)


def get_user_agent():
    user_agents = []
    with open('user_agents.txt', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.strip():
                user_agents.append(line.strip())
    return choice(user_agents)


def check_review(cookies, article):
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/product/comments/goods',
                data={
                    'limit': 150,
                    'type': 'all',
                    'status': '544'
                },
                cookies=cookies,
                params={
                    'nmId': article
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом product/comments/goods: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return True
        return False
    return None


def get_reviews(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    reviews = []
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/lk/myorders/archive/get',
                data={
                    'limit': 150,
                    'type': 'all',
                    'status': '544'
                },
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом lk/myorders/archive/get: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0 and 'value' in response:
            if 'archive' in response['value']:
                for value in response['value']['archive']:
                    check_result = check_review(cookies, value['code1S'])
                    reviews.append([value['code1S'], check_result, value['name'], value['price'], value['imtId'],
                                    value['size'] if 'size' in value else None])
                return reviews
    return None


def get_account_info(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    account_data = {}
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/personalinfo',
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом personalinfo: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            if 'value' in response:
                response = response['value']
                account_data['account_number'] = profile_name
                if 'fullName' in response:
                    full_name = response['fullName'] if len(response['fullName']) > 0 else f'Аккаунт {profile_name}'
                    account_data['full_name'] = full_name
                if 'formattedPhoneMobile' in response:
                    phone_number = response['formattedPhoneMobile']
                    account_data['phone_number'] = phone_number
                if 'purchaseAmount' in response:
                    ransom_sum = response['purchaseAmount']
                    account_data['ransom_sum'] = ransom_sum
                if 'personalDiscount' in response:
                    wb_sale = response['personalDiscount']
                    account_data['wb_sale'] = wb_sale
                break
    else:
        return None
    if len(list(account_data.keys())) == 0:
        return None
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/account/getsignedbalance',
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом account/getsignedbalance: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            if 'value' in response and 'moneyBalance' in response['value']:
                balance = response['value']['moneyBalance']
                account_data['balance'] = balance
                break
    else:
        balance = 'Не удалось определить'
        account_data['balance'] = balance
    return account_data


def get_account_balance(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/account/getsignedbalance',
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом account/getsignedbalance: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            if 'value' in response and 'moneyBalance' in response['value']:
                balance = response['value']['moneyBalance']
                break
    else:
        balance = 'Не удалось определить'
    return balance


def get_money(profile_name, balance):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/lk/mywallet/funds/card/transfer',
                cookies=cookies,
                data={
                    'amount': balance,
                    'cardId': 'sbp'
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом account/getsignedbalance: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return True
    return False


def change_address(profile_name, address):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://ru-basket-api.wildberries.ru/spa/poos/create?version=1',
                cookies=cookies,
                data={
                    'Item.AddressId': address
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /spa/poos/create?version=1: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            break
    else:
        return False
    for i in range(3):
        try:
            response = requests.post(
                'https://ru-basket-api.wildberries.ru/spa/address/select',
                cookies=cookies,
                data={
                    'addressId': address,
                    'deliveryWay': 'self'
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /spa/address/select: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return True
    return False


def change_name(profile_name, name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.patch(
                'https://www.wildberries.ru/webapi/personalinfo/fio',
                cookies=cookies,
                data=json.dumps({
                    'firstName': name
                }),
                headers={
                    'Content-Type': 'application/json'
                }
            )
            response = response.json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/personalinfo/fio: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            break


def send_review(account_name, article, review_text, review_number, images, profile_name, link, size):
    if len(account_name) > 0:
        change_name(profile_name, account_name)
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/spa/product/predictcomment',
                cookies=cookies,
                data=json.dumps({
                    'text': review_text,
                    'code1S': article
                })
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/personalinfo/fio: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            break
    data = {
        'cod1s': article,
        'link': link,
        'rating': review_number,
        'sizeMatch': None,
        'sizeName': size,
        'text': review_text,
        'visibility': 1
    }
    if len(images) > 0:
        data['userPhotos'] = images
    for _ in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/product/comments',
                cookies=cookies,
                data=json.dumps(data),
                headers={
                    'Content-Type': 'application/json'
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/product/comments: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return True
    return False


def get_nm_id(article):
    def volHostV2(e):
        if e >= 0 and e <= 143:
            return "//basket-01.wb.ru/"
        elif e >= 144 and e <= 287:
            return "//basket-02.wb.ru/"
        elif e >= 288 and e <= 431:
            return "//basket-03.wb.ru/"
        elif e >= 432 and e <= 719:
            return "//basket-04.wb.ru/"
        elif e >= 720 and e <= 1007:
            return "//basket-05.wb.ru/"
        elif e >= 1008 and e <= 1061:
            return "//basket-06.wb.ru/"
        elif e >= 1062 and e <= 1115:
            return "//basket-07.wb.ru/"
        elif e >= 1116 and e <= 1169:
            return "//basket-08.wb.ru/"
        elif e >= 1170 and e <= 1313:
            return "//basket-09.wb.ru/"
        elif e >= 1314 and e <= 1601:
            return "//basket-10.wb.ru/"
        elif e >= 1602 and e <= 1655:
            return "//basket-11.wb.ru/"
        elif e >= 1656 and e <= 1919:
            return "//basket-12.wb.ru/"
        else:
            return "//basket-13.wb.ru/"
    for i in range(3):
        try:
            response = requests.get(
                f'https:{volHostV2(int(article) // 100000)}vol{article[:3]}/part{article[:5]}/{article}/info/ru/card.json',
                headers={
                    'Content-Type': 'application/json'
                }
            )
            response = response.json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом получения nm_id: {error}')
            time.sleep(1)
            continue
        if 'nm_id' in response:
            return response['nm_id']
    return None


def get_size(article):
    for i in range(3):
        try:
            response = requests.get(
                f'https://card.wb.ru/cards/detail?appType=1&curr=rub&nm={article}',
                headers={
                    'Content-Type': 'application/json'
                }
            )
            response = response.json()
            return response['data']['products'][0]['sizes'][0]['optionId']
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом получения nm_id: {error}')
            time.sleep(1)
            continue
    return None


def get_browser(profile_name, cookies, change_ip=True):
    if change_ip is True:
        try:
            print(requests.get(get_settings('SETTINGS', 'proxy_change_url'),
                               headers={
                                   'User-Agent': get_user_agent()
                               }).text)
        except Exception as error:
            print('Прокси:', error)
    PROXY_HOST = get_settings('SETTINGS', 'PROXY_HOST')
    PROXY_PORT = int(get_settings('SETTINGS', 'PROXY_PORT'))
    PROXY_USER = get_settings('SETTINGS', 'PROXY_USER')
    PROXY_PASS = get_settings('SETTINGS', 'PROXY_PASS')

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    options = webdriver.ChromeOptions()
    pluginfile = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    options.add_extension(pluginfile)
    data = json.loads(open('user_agents.json', 'r', encoding='utf-8').read())
    if not profile_name in data:
        user_agent = get_user_agent()
    else:
        user_agent = data[profile_name]
    options.add_argument(f'user-agent={user_agent}')
    #options.add_argument("--headless")
    #options.add_argument('--no-sandbox')
    #browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    browser = webdriver.Chrome(service=Service(executable_path='chromedriver'), options=options)
    browser.maximize_window()
    browser.get('https://www.wildberries.ru/lk/basket')
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.get('https://www.wildberries.ru/lk/basket')
    if not profile_name in data:
        return browser, user_agent
    else:
        return browser, None


def get_ransom(profile_name, article, address):
    change_address(profile_name, address)
    browser, user_agent = get_browser(profile_name, pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")))
    browser.get('https://www.wildberries.ru/lk')
    time.sleep(5)
    with open('html1.html', 'w', encoding='utf-8') as file:
        file.write(browser.page_source)
    browser.get(f'https://www.wildberries.ru/catalog/{article}/detail.aspx')
    for i in range(20):
        try:
            button = browser.find_element(By.CLASS_NAME, 'product-page__order-container').find_element(By.CLASS_NAME, 'order__btn-buy')
            browser.execute_script('arguments[0].click();', button)
            break
        except Exception as error:
            logger.error(f'Попытка {i+1}. Ошибка при нажатии на кнопку "Купить сейчас". Артикул {article}. Аккаунт {profile_name}: {error}')
        time.sleep(1)
    else:
        logger.error(f'Ошибка при нажатии на кнопку "Купить сейчас". Артикул {article}. Аккаунт {profile_name}')
        browser.quit()
        return False
    for i in range(20):
        try:
            button = browser.find_element(By.CLASS_NAME, 'sidebar__sticky-wrap').find_element(By.NAME, 'ConfirmOrderByRegisteredUser')
            browser.execute_script('arguments[0].click();', button)
            break
        except Exception as error:
            logger.error(f'Попытка {i+1}. Ошибка при нажатии на кнопку "Оплатить заказ". Артикул {article}. Аккаунт {profile_name}: {error}')
        time.sleep(1)
    else:
        logger.error('Не удалось нажать на кнопку "Оплатить заказ" после 20 попыток.')
        with open('html.html', 'w', encoding='utf-8') as file:
            file.write(browser.page_source)
        browser.quit()
        return False
    time.sleep(3)
    browser.quit()
    buy_articles = Account.objects.filter(profile_name=int(profile_name))[0].buy_articles
    buy_articles.append(int(article))
    Account.objects.filter(profile_name=int(profile_name)).update(buy_articles=buy_articles)
    address = Address.objects.filter(address_id=int(address))[0]
    Ransoms.objects.create(
        profile_name=profile_name,
        article=article,
        ransom_date=datetime.datetime.now(),
        address=address.address_name
    )
    return True


def check_payment(profile_name, payment_url, article, address):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(20):
        try:
            response = requests.post(
                payment_url,
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/personalinfo/fio: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            if 'value' in response and response['value']['status'] == 'success':
                Account.objects.filter(profile_name=int(profile_name)).update(payment_qr=True)
                for i in range(3):
                    result = get_ransom(profile_name, article, address)
                    if result:
                        return True
        time.sleep(3)
    return False


def get_qr_code(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://ru-basket-api.wildberries.ru/webapi/lk/account/spa/bindnewsbp',
                cookies=cookies,
                data=json.dumps({
                    'returnUrl': 'https://www.wildberries.ru/lk/details#bankCard',
                    'balanceAmount': 'undefined'
                })
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/personalinfo/fio: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return response['value']['qrCode'], f'https://www.wildberries.ru{response["value"]["checkUrl"]}'
    return False, False


def get_user_id(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/personalinfo',
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/basket/info: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return response['value']['id']
    return False


def get_code(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    products = []
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/lk/myorders/delivery/code',
                cookies=cookies,
                data={
                    'wbxUserId': 1
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/basket/info: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            return response['value']['privateCode'], response['value']['qrCode']
    return False, False


def get_delivery(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    products = []
    for i in range(3):
        try:
            response = requests.post(
                'https://www.wildberries.ru/webapi/v2/lk/myorders/delivery/active',
                cookies=cookies
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/basket/info: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            for delivery in response['value']['positions']:
                if delivery['trackingStatus'] == 'Готов к выдаче':
                    products.append([delivery['address'], delivery['name'], delivery['code1S']])
            break
    if len(products) > 0:
        code, qr_code = get_code(profile_name)
        if code and qr_code:
            return products, code, qr_code
    return False, False, False


def delete_payment(profile_name):
    cookies = {}
    for cookie in pickle.load(open(f"wb_applications/static/cookies_{profile_name}.pkl", "rb")):
        cookies[cookie['name']] = cookie['value']
    card_id = []
    for i in range(3):
        try:
            response = requests.post(
                'https://ru-basket-api.wildberries.ru/webapi/lk/bankcards',
                cookies=cookies,
                data={
                    'currency': 'RUB',
                    'bypassCache': False
                }
            ).json()
        except Exception as error:
            logger.error(f'Ошибка при работе с запросом /webapi/lk/bankcards: {error}')
            time.sleep(1)
            continue
        if 'resultState' in response and response['resultState'] == 0:
            for card in response['value']['maskedCards']:
                card_id.append(card['id'])
    for card in card_id:
        for i in range(3):
            try:
                response = requests.post(
                    'https://ru-basket-api.wildberries.ru/webapi/lk/account/spa/deletecards',
                    cookies=cookies,
                    data={
                        'cardIds[0]': card,
                        'paymentCode': 'crd'
                    }
                ).json()
            except Exception as error:
                logger.error(f'Ошибка при работе с запросом /webapi/lk/account/spa/deletecards: {error}')
                time.sleep(1)
                continue
            if 'resultState' in response and response['resultState'] == 0:
                break
    return True
