from classes import MetroPars

if __name__ == '__main__':
    max_pages = int(input("Количество выводимых страниц: "))
    parser = MetroPars(max_pages)
    parser.parse()
    parser.save_to_json("src/products.json")
    parser.save_to_csv("src/products.csv")
    print("\nОбъекты загружены и сохранены.")
