import fake_headers
import requests
from bs4 import BeautifulSoup
import pprint
import json

# для подмены заголовков, типа мы браузер хром.
def gen_headers():
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()

# Получаем данные из источника. Применяем gen_headers() что бы HH нас не банил.
full_response = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2", headers=gen_headers())
# Получаем содержимое страницы в текстовом виде
full_response_text = full_response.text
# Обработай содержимое переменной с помощью lxml движка
vacancies_soup = BeautifulSoup(full_response_text, "lxml")
# Находим все вакансии. Должны получить список.   sticky-sidebar-and-content--NmOyAQ7IxIOkgRiBRSEg

vacancies_list_tag = vacancies_soup.find("main", class_="vacancy-serp-content")
# Список вакансий.
vacancies_data = []
# Найди в списке вакансий тег div, class_="serp-item" и проитерируйся по нему.
for vacancies in vacancies_list_tag.find_all("div", class_="serp-item"):
    # Список характеристик вакансии.
    vacancy_data = {}

    # Найди в каждой вакансии название вакансии.
    header = vacancies.find("h3", class_="bloko-header-section-3")
    header_text = header.text
    # print(f"вакансия: {header_text}")
    vacancy_data["position"] = header_text

    # Найти ссылку
    almost_link = header.find("a", class_="bloko-link")
    # Конкретно ссылка находится в 'href'
    link = almost_link["href"]
    # print(f"ссылка: {link}")
    vacancy_data["link"] = link

    # Проходим по ссылке отдельной вакансии.
    vacancy_response = requests.get(link, headers=gen_headers())
    # Получаем содержимое страницы в текстовом виде
    vacancy_res_text = vacancy_response.text
    # Обрабатываем содержимое переменной с помощью lxml движка
    vacancy_soup = BeautifulSoup(vacancy_res_text, "lxml")

    # Получаем описание вакансии.
    vacancies_content = vacancy_soup.find("div", class_="g-user-content")
    if vacancies_content is not None:
        vacancies_content_text = vacancies_content.text
        # print(vacancies_content_text)
    else:
        print("Не успел загрузить.")

    # Если в вакансии есть ключевые слова.
    if "Django" and "Flask" in vacancies_content_text:

        # Найди вилку з.п.
        salary = vacancy_soup.find("span", {"data-qa": "vacancy-salary-compensation-type-net"})
        if salary is not None:
            salary_text = salary.text
            # print(f"зарплатная вилка: {salary_text}")
            vacancy_data["salary"] = salary_text
        else:
            # print("Заработная вилка не указана.")
            vacancy_data["salary"] = "Заработная вилка не указана."

        # Найти имя компании
        company_name = vacancy_soup.find("span",{"data-qa": "bloko-header-2"})
        if company_name is not None:
            company_name_text = company_name.text
            # print(f"Название компании: {company_name_text}")
            vacancy_data["company_name"] = company_name_text
        else:
            # print("Название компании не указано.")
            vacancy_data["company_name"] = "Название компании не указано."

        # Найти город
        sity = vacancy_soup.find("span", {"data-qa": "vacancy-view-raw-address"})
        if sity is not None:
            sity_text = sity.text
            # print(f"Название города: {sity_text.split(',')[0]}")
            vacancy_data["sity"] = sity_text.split(',')[0]
        else:
            # print("Город не указан.")
            vacancy_data["sity"] = "Город не указан."
        # print( )

        vacancies_data.append(vacancy_data)

# pprint.pprint(vacancies_data)
# print(type(vacancies_data))

json_string = json.dumps(vacancies_data, ensure_ascii=False)
pprint.pprint(json_string)

with open('output.json', 'w', encoding='UTF-8') as f:
    json.dump(vacancies_data, f, ensure_ascii=False)
