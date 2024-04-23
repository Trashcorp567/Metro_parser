import json
import requests
from bs4 import BeautifulSoup
import csv
import re
import sys


class MetroPars:
    def __init__(self, max_pages):
        self.max_pages = max_pages
        self.base_url = "https://online.metro-cc.ru"
        self.total_products = []
        self.total_count = 0

    # Метод, для опеределения кол-ва страниц, на которых будет произведен поиск (на одной странице 30 объектов)
    def parse(self):
        print("Выполнение...")
        pages = 1
        while pages <= self.max_pages:
            answer = requests.get(f"https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?page={pages}")
            soup = BeautifulSoup(answer.text, "html.parser")
            pages += 1
            products = soup.find('div', class_='subcategory-or-type__products')
            if not products:
                print("Страницы закончились. Завершение работы.")
                break
            elif answer.status_code == 200:
                current_product = 0
                for product in products:
                    current_product += 1
                    current_progress = (self.total_count / (self.max_pages * 30)) * 100

                    # Прогресс выгрузки
                    sys.stdout.write(f"\rЗагрузка: {current_progress:.2f}%")
                    sys.stdout.flush()

                    # Извлекаем название товара
                    name_elem = product.find('span', class_='product-card-name__text')
                    if name_elem:
                        name = name_elem.text.strip()
                    else:
                        continue

                    # Извлекаем ссылку на товар
                    link_elem = product.find('a', class_='product-card-name')
                    link = link_elem.get('href') if link_elem else "Ссылка не найдена"

                    # Создаём ссылку на конкретный товар для последующего обращения
                    base = self.base_url + link

                    # Создаём запрос на отдельный товар для извлечения бренда
                    new_answer = requests.get(base)
                    soup2 = BeautifulSoup(new_answer.text, "html.parser")
                    brand_elem = soup2.find_all('span', class_='product-attributes__list-item-name-text')
                    for brand in brand_elem:
                        if brand.get_text(strip=True) == 'Бренд':
                            next_tag = brand.find_next('a')
                            if next_tag:
                                brands = next_tag.get_text(strip=True)
                            else:
                                brands = "Бренд не найден"

                    # Извлекаем id товара по его Артикулу
                    article_elem = soup2.find_all('p', class_='product-page-content__article')
                    for id in article_elem:
                        if 'Артикул' in id.get_text():
                            match = re.search(r'Артикул:\s*(\d+)', id.get_text())
                            if match:
                                product_id = match.group(1)
                            else:
                                product_id = "Артикул не найден"
                            break

                    # Извлекаем текущую стоимость товара
                    discount_price_elem = product.find('span', class_='product-price__sum-rubles')
                    discount_price = discount_price_elem.text.strip() if discount_price_elem else "Цена не указана"

                    # Извлекаем стоимость товара без скидки
                    price_elem = product.find('div', class_='product-unit-prices__old-wrapper')
                    price_text = price_elem.text.strip() if price_elem else "Цена не указана"
                    match = re.search(r'\d[\d\s,]*', price_text)
                    price = match.group() if match else "Цена не указана"

                    # Сохраняем объекты для дальнейшей записи в файл
                    self.total_products.append({
                        "id": product_id,
                        "name": name,
                        "link": base,
                        "discount_price": discount_price,
                        "price": price,
                        "brand": brands
                    })
                    self.total_count += 1

    def save_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.total_products, f, ensure_ascii=False, indent=4)

    def save_to_csv(self, filename):
        keys = self.total_products[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.total_products)
