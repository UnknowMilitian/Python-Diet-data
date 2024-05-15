import os
import csv
import json
import requests
from bs4 import BeautifulSoup

url = "https://health-diet.ru/table_calorie"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

req = requests.get(url, headers=headers)

with open("index.html", "w", encoding="utf-8") as file:
    file.write(req.text)

with open("index.html", "r", encoding="utf-8") as file:
    src = file.read()

# ----- Working with data -----

soup = BeautifulSoup(src, "lxml")

# Finding all Categories a-tags and hrefs
all_categories_dict = {}

for i in soup.find_all("a", class_="mzr-tc-group-item-href"):
    item_text = i.text
    item_href = "https://health-diet.ru" + i.get("href")

    all_categories_dict[item_text] = item_href

# Ensure the directories exist
os.makedirs("data", exist_ok=True)

# Writing all categories
with open("all_categories_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open("all_categories_dict.json", encoding="utf-8") as file:
    all_categories = json.load(file)

count = 0

for categorie_title, categorie_href in all_categories.items():
    rep = [" ", "-", ",", "'"]
    for item in rep:
        if item in categorie_title:
            categorie_title = categorie_title.replace(item, "_")

    req = requests.get(categorie_href, headers=headers)
    src = req.text

    with open(
        f"data/{count}_{categorie_title}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(src)

    with open(
        f"data/{count}_{categorie_title}.html",
        "r",
        encoding="utf-8",
    ) as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Testing
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # Taking tables
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(
        f"data/{count}_{categorie_title}.csv",
        "w",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow((product, calories, proteins, fats, carbohydrates))

    # Taking data
    product_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []

    for item in product_data:
        product_tds = item.find_all("td")

        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates,
            }
        )

        with open(
            f"data/{count}_{categorie_title}.csv",
            "a",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow((title, calories, proteins, fats, carbohydrates))

    with open(
        f"data/{count}_{categorie_title}.json",
        "a",
        encoding="utf-8",
    ) as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
