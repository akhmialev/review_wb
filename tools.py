import openpyxl
from fake_useragent import UserAgent

ua = UserAgent()
headers = {'User-Agent': ua.random}


def read_xlsx(file_path):
    """
        Функция читает наш xlsx файл
    :param file_path: путь к файлу
    """
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    sku_list = []
    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            sku_list.append(cell)
    workbook.close()
    return sku_list
