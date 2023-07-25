import random
import time
from django.shortcuts import render
import wb_api
import os
import wb_selenium_tools
from django.core.files.storage import FileSystemStorage
import threading
from .models import Review, Address, Account, Ransoms
import base64


# Create your views here.
def index(request):
    accounts_list = Account.objects.all()
    accounts = []
    for account in accounts_list:
        if account.active:
            accounts.append([account.profile_name, 'Привязан СБП' if account.payment_qr else 'Не привязан СБП',
                             ", ".join([str(value) for value in account.buy_articles]),
                             f'/cookies_{account.profile_name}.pkl'])
    if request.method == 'POST':
        for key in request.POST:
            if key.startswith('del_'):
                profile_name = key.split('_')[1]
                wb_api.delete_payment(profile_name)
                Account.objects.filter(profile_name=profile_name).update(payment_qr=False)
    return render(request, 'index.html', context={'accounts': accounts})


def get_money(request):
    modal_window, result, message = False, False, None
    if request.method == 'POST':
        for label in request.POST:
            if label.startswith('get-money'):
                account_number = label.split('_')[1]
                balance = label.split('_')[2]
                modal_window = True
                if balance != '0':
                    result = wb_api.get_money(account_number, balance)
                    if result:
                        message = f'Успешно вывел {balance} руб. с аккаунта {account_number}'
                    else:
                        message = f'Ошибка при выводе {balance} руб. с аккаунта {account_number}'
                else:
                    message = 'Нельзя вывести 0 руб.!'
    accounts_list = Account.objects.all()
    accounts = []
    for account in accounts_list:
        if account.active:
            account_balance = wb_api.get_account_balance(account.profile_name)
            accounts.append({
                'full_name': f'Аккаунт {account.profile_name}',
                'balance': account_balance,
                'account_number': account.profile_name
            })
    return render(request, 'get-money.html', context={'accounts': accounts, 'modal_window': modal_window,
                                                      'message': message})


def send_reviews(request):
    reviews_data = {}
    articles = {}
    for obj in Review.objects.all():
        if not obj.account in articles:
            articles[obj.account] = [obj.article]
        else:
            articles[obj.account].append(obj.article)
    for file in os.listdir('wb_applications/static'):
        if file.endswith('.pkl') and file.startswith('cookies_'):
            account_number = file.split('cookies_')[1].split('.pkl')[0]
            reviews = wb_api.get_reviews(account_number)
            for review in reviews:
                if review[1] is True:
                    if (int(account_number) in articles and int(review[0]) not in articles[int(account_number)]) or \
                            int(account_number) not in articles:
                        Review.objects.create(
                            article=review[0],
                            imt_id=review[4],
                            size=review[5],
                            account=int(account_number),
                            user_name=None,
                            review_text=None,
                            review_number=None,
                            review_image=None,
                            status=False
                        )
                    if review[0] not in reviews_data:
                        reviews_data[review[0]] = {
                            'price': review[3],
                            'name': review[2],
                            'count': 1
                        }
                    else:
                        reviews_data[review[0]]['count'] += 1
    return render(request, 'reviews.html', context={'reviews': reviews_data})


def review_pattern(request):
    return render(request, 'review_pattern.html')


def register_accounts(request):
    if request.method == 'GET':
        return render(request, 'register_account.html', context={'method': 'GET', 'modal': False})
    elif request.method == 'POST':
        account_count = request.POST['account_count']
        activate_type = request.POST['activate']
        threading.Thread(target=wb_selenium_tools.register_accounts, args=(account_count, activate_type,)).start()
        return render(request, 'register_account.html', context={'method': 'POST', 'count': account_count, 'modal': True})


def send_review(request, article):
    if request.method == 'POST':
        images = []
        if request.FILES:
            for file in request.FILES.getlist('images'):
                fs = FileSystemStorage()
                filename = fs.save(f'wb_applications/images/{file.name}', file)
                with open(filename, 'rb') as img_file:
                    images.append(base64.b64encode(img_file.read()).decode('utf-8'))
        account_name = request.POST['accountName']
        if len(account_name) == 0:
            account_name = random.choice(
                ['Александр', 'Михаил', 'Максим', 'Лев', 'Марк', 'Артем', 'Иван', 'Матвей']
            )
        review_text = request.POST['reviewText']
        review_number = request.POST['reviewNumber']
        profile_name = Review.objects.filter(article=int(article))
        if len(profile_name) > 0:
            profile_name = profile_name[0]
            status = wb_api.send_review(account_name, article, review_text, review_number, images, profile_name.account,
                                        profile_name.imt_id, profile_name.size)
            if status:
                Review.objects.filter(id=profile_name.id).update(
                    user_name=account_name,
                    review_text=review_text,
                    review_number=review_number,
                    review_image=images,
                    status=True
                )
                return render(request, 'send_review.html', context={
                    'article': article,
                    'modal_window': True,
                    'message': f'Отзыв на артикул {article} был успешно отправлен с аккаунта {profile_name.account}'
                })
            else:
                return render(request, 'send_review.html', context={
                    'article': article,
                    'modal_window': True,
                    'message': f'Ошибка при отправке отзыва на артикул {article} с аккаунта {profile_name.account}'
                })
    return render(request, 'send_review.html', context={
        'article': article,
        'modal_window': False
    })


def get_ransoms(request):
    options = []
    address = Address.objects.all()
    for option in address:
        options.append([option.address_id, option.address_name])
    ransoms_list = Ransoms.objects.order_by('-ransom_date')
    ransoms = []
    for ransom in ransoms_list:
        ransoms.append([ransom.profile_name, ransom.article, ransom.ransom_date.strftime('%d-%m-%Y %H:%M:%S'),
                        ransom.address])
        if len(ransoms) == 300:
            break
    if request.method == 'POST':
        if 'article' in request.POST:
            article = request.POST['article']
            address = request.POST['address']
            accounts_list = Account.objects.all()
            for account in accounts_list:
                if account.buy_articles is None or not int(article) in account.buy_articles:
                    if account.payment_qr is False:
                        qr_code, payment_url = wb_api.get_qr_code(account.profile_name)
                        return render(request, 'buy.html', context={'options': options,
                                                                    'modal_window': True,
                                                                    'message': 'Оплатите следующий QR для привязки счета СБП',
                                                                    'qr_code': qr_code,
                                                                    'profile_name': account.profile_name,
                                                                    'article': article,
                                                                    'payment_url': payment_url,
                                                                    'address': address,
                                                                    'ransoms': ransoms})
                    else:
                        threading.Thread(target=wb_api.get_ransom, args=(account.profile_name, article, address,)).start()
                        return render(request, 'buy.html', context={'options': options,
                                                                    'modal_window': True,
                                                                    'message': 'Ожидайте, товар скоро появится на странице с выкупами.',
                                                                    'ransoms': ransoms
                                                                    })
        else:
            for key in request.POST:
                if key.startswith('success_'):
                    profile_name = key.split('___')[1]
                    article = key.split('___')[2],
                    payment_url = key.split('___')[3]
                    address = key.split('___')[4]
                    threading.Thread(target=wb_api.check_payment, args=(profile_name, payment_url, article[0], address,)).start()
                    return render(request, 'buy.html', context={'options': options,
                                                                'modal_window': True,
                                                                'message': 'Ожидайте, товар скоро появится на странице с выкупами.',
                                                                'ransoms': ransoms
                                                                })
    return render(request, 'buy.html', context={'options': options, 'ransoms': ransoms})


def get_codes(request):
    accounts, text = [], ''
    for file in os.listdir('wb_applications/static'):
        if file.endswith('.pkl') and file.startswith('cookies_'):
            account_number = file.split('cookies_')[1].split('.pkl')[0]
            if account_number.isdigit():
                products, code, qr_code = wb_api.get_delivery(account_number)
                if products and code and qr_code:
                    for product in products:
                        accounts.append([account_number, product[0], product[1], product[2], code, qr_code])
                        text += f'{product[0]} | {account_number} | {code}\n'
    return render(request, 'get_codes.html', context={'accounts': accounts, 'text': text.strip()})