from datetime import datetime

from config import file_path
from tools import read_xlsx, get_json


def create_dict_for_get_reviews():
    """
        Функция для формирования словаря где key - id(sku) товара, value - root (это значение по которому можно
        обратиться к api wb для получения всех отзывов).
    """
    sku_list = read_xlsx(file_path)
    root_dct = {}
    for sku in sku_list:
        url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1257786' \
              f'&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,22,110,48,71,114&spp=0&nm={sku}'
        data = get_json(url)
        root = data['data']['products'][0]['root']
        root_dct.update({str(sku): str(root)})
    return root_dct


def create_list_urls_for_get_reviews():
    """
        Функция для создания списка корректных урлов, по которым можно будет работать с отзывами.
    """
    root_dct = create_dict_for_get_reviews()
    review_list = []
    for i in range(1, 3):
        for k, v in root_dct.items():
            url = f'https://feedbacks{str(i)}.wb.ru/feedbacks/v1/{v}'
            data = get_json(url)
            check_on_json = (data['photosUris'])
            if check_on_json:
                review_list.append(url)
    return review_list


def get_data():
    """
        Функция собирает комментарии за сегодняшний день с рейтингом от 1 до 4 звезд
    """
    urls = create_list_urls_for_get_reviews()

    today_bad_feedbacks = []
    bad_sku = []
    for url in urls:
        data = get_json(url)
        current_date = datetime.now().date()

        for feedback in data['feedbacks']:
            if current_date == datetime.strptime(feedback["createdDate"], "%Y-%m-%dT%H:%M:%SZ").date():
                if feedback['productValuation'] < 5:
                    today_bad_feedbacks.append(feedback)
                    if (feedback['nmId']) not in bad_sku:
                        bad_sku.append((feedback['nmId']))
    return today_bad_feedbacks


def get_data_for_bot():
    """
        Функция собирает список строк для отправки в телеграм боте
    """
    feedbacks = get_data()
    string_for_bot = []
    for feedback in feedbacks:
        sku_product = feedback['nmId']
        review_text = ' '.join(feedback['text'].split('\n'))

        url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1257786&' \
              f'regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,22,110,48,71,114&spp=0&nm={str(sku_product)}'
        data = get_json(url)
        name_of_product = data['data']['products'][0]['name']
        brand = data['data']['products'][0]['brand']
        review_rating = data['data']['products'][0]['reviewRating']
        product_valuation = feedback['productValuation']
        string_for_bot.append(
            f'Негативный отзыв: {name_of_product} {brand}, SKU:{sku_product}, звезд: {product_valuation},'
            f'отзыв:{review_text}, оценка:{review_rating} ')
    return string_for_bot

get_data_for_bot()