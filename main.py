import bs4
import requests

from fake_headers import Headers
from pydantic import BaseModel

green = "\033[92m"
white = "\033[0m"


class VacancyInfo(BaseModel):
    url: str
    salary: str
    company: str
    city: str


class Vacancies(BaseModel):
    vacancies: list[VacancyInfo]



def parser():
    search_results = Vacancies(vacancies=[])

    response = make_request(request_link)
    soup_text = bs4.BeautifulSoup(response.text, 'lxml')

    for vacancy in soup_text.find_all("a", class_="serp-item__title"):
        search_results.vacancies.append(parse_vacancy(vacancy["href"]))

    save_vacancies(search_results)

    print(f"{green}Вакансии успешно сохранены!{white}")


def parse_vacancy(url: str) -> VacancyInfo:

    response = make_request(url)
    soup_text = bs4.BeautifulSoup(response.text, 'lxml')

    description = soup_text.find_all("span", class_="bloko-header-section-2 bloko-header-section-2_lite")
    location = soup_text.find_all("p", attrs={"data-qa": "vacancy-view-location"})

    salary = get_salary(description)
    company = get_company(description)
    city = get_city(location, soup_text)

    return VacancyInfo(url=url, salary=salary.replace("\xa0", " ") + " руб.", company=company, city=city)


def get_salary(description: bs4.element.ResultSet) -> str:
    return description[0].text.split("₽")[0].strip() if len(description) == 2 else "Зарплата не указана"


def get_company(description: bs4.element.ResultSet) -> str:
    return description[1].text.strip() if len(description) == 2 else description[0].text.strip()


def get_city(location: bs4.element.ResultSet, soup_text: bs4.BeautifulSoup) -> str:
    if location:
        return location[0].text.strip()
    else:
        full_address = soup_text.find_all("span", attrs={"data-qa": "vacancy-view-raw-address"})
        return full_address[0].text.split(",")[0]


def make_request(url: str) -> requests.Response:
    return requests.get(url, headers=headers.generate())


def save_vacancies(vacancies: Vacancies) -> None:
    with open("vacancies.json", "w") as file:
        file.write(vacancies.model_dump_json())


if __name__ == "__main__":
    headers = Headers(browser='chrome', os='win')
    request_link = "https://hh.ru/search/vacancy?text=Python+django+flask&from=suggest_post&salary=&area=1&area=2&ored_clusters=true"

    parser()

