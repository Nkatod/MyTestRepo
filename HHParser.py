import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pandas import DataFrame
from concurrent.futures import ThreadPoolExecutor
import re

urlhh = 'https://hh.ru'
url_moscow = 'https://hh.ru/search/resume?area=1&specialization=1&salary_from=100000&salary_to=&' \
             'label=only_with_salary&gender=unknown&age_from=&age_to=&text=Python&isDefaultArea=true' \
             '&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=false&st=resumeSearch&page='
url_kiev = 'https://hh.ru/search/resume?text=Python&st=resumeSearch&logic=normal&pos=full_text&' \
           'exp_period=all_time&exp_company_size=any&exp_industry=any&specialization=1&area=115&' \
           'relocation=living_or_relocation&salary_from=1500&salary_to=&currency_code=RUR&' \
           'label=only_with_salary&experience=moreThan6&education=none&age_from=&age_to=&' \
           'gender=unknown&order_by=relevance&search_period=0&items_on_page=50&no_magic=false&page='

url_moscow_vacancies = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=true&' \
                       'enable_snippets=true&no_magic=true&search_field=name&' \
                       'search_field=description&search_period=30&items_on_page=100&text=Python&page='

# url_moscow_vacancies = 'https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&' \
#                        'ored_clusters=true&schedule=remote&text=Python&search_period=30&page='

resumes = []
positions = []
ref_list = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.473',
}

maxWorkers = 4
executor = ThreadPoolExecutor(max_workers=maxWorkers)
loop = asyncio.get_event_loop()


class Currencies:

    def __init__(self):
        self._usd = 75
        self._eur = 90
        self._grivna = 2.66

    @property
    def usd(self):
        return self._usd

    @property
    def eur(self):
        return self._eur

    @property
    def grivna(self):
        return self._grivna


async def parse_search(url, semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status, url)
                htmltext = await resp.text()
                # soup = BeautifulSoup(htmltext, 'html.parser')
                args = []
                args.append(htmltext)
                args.append('html.parser')
                soup = await loop.run_in_executor(executor, BeautifulSoup, *args)
                items = soup.find_all('div', class_='resume-search-item')
                for item in items:
                    href = item.find('a', class_='resume-search-item__name').attrs['href']
                    ref_list.append(urlhh + href)


async def parse_positions(url, semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status, url)
                htmltext = await resp.text()
                args = []
                args.append(htmltext)
                args.append('html.parser')
                soup = await loop.run_in_executor(executor, BeautifulSoup, *args)
                items = soup.find_all('div', class_='vacancy-serp-item')
                for item in items:
                    href = item.find('a', class_='bloko-link HH-LinkModifier')
                    if href is None:
                        href = item.find('a')
                    if href is None:
                        href = 'Error'
                    else:
                        href = href.attrs['href']
                    ref_list.append(href)
                await asyncio.sleep(1)


def anketa_processor(htmltext, url):
    soup = BeautifulSoup(htmltext, 'html.parser')
    title = soup.find_all('span', class_='resume-block__title-text')[0].text
    salary = clean_salary(soup)
    exp_age = clean_exp_age(soup)
    age = clean_age(soup)
    atr_list = [''] * 10
    atr_items = soup.find_all('div', class_='bloko-tag bloko-tag_inline bloko-tag_countable')
    i = 0
    for item in atr_items:
        try:
            atr_list[i] = item.text
            i += 1
        except Exception as exc:
            break
    atr_list.sort(reverse=True)
    return {
        'title': title,
        'salary_min': salary,
        'salary_max': salary,
        'age': age,
        'exp_age': exp_age,
        'attr0': atr_list[0],
        'attr1': atr_list[1],
        'attr2': atr_list[2],
        'attr3': atr_list[3],
        'attr4': atr_list[4],
        'attr5': atr_list[5],
        'attr6': atr_list[6],
        'attr7': atr_list[7],
        'attr8': atr_list[8],
        'attr9': atr_list[9],
        'ref': url,
    }


def get_description_from_soup(soup):
    result = ''
    desc_arr = soup.find_all('div', class_='g-user-content')

    for el in desc_arr:
        result += el.text

    return result


def count_english(description: str) -> float:
    result = 0
    if len(description) == 0:
        return result
    description = description.lower()
    all_letters = set('abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя .,')
    new_desc = [x for x in description if x in all_letters]

    engl_set = set('abcdefghijklmnopqrstuvwxyz')
    for letter in new_desc:
        if letter in engl_set:
            result += 1
    q_letters = len(new_desc)
    if q_letters == 0:
        q_letters = 1
    result = result / q_letters
    result = round(result, 3)
    return result


def position_processor(htmltext, url):
    soup = BeautifulSoup(htmltext, 'html.parser')
    title = soup.find_all(attrs={'data-qa': 'vacancy-title'})[0].text
    salary = clean_position_salary(soup.find_all('span', class_='bloko-header-2 bloko-header-2_lite')[0].text)
    exp_age = clean_exp_age(soup)
    age = clean_age(soup)
    atr_list = [''] * 10
    atr_items = soup.find_all('div', class_='bloko-tag bloko-tag_inline bloko-tag_countable')
    company_name_set = soup.find_all('a', class_='vacancy-company-name')
    company_name = ''
    if len(company_name_set) > 0:
        company_name = company_name_set[0].text

    description = get_description_from_soup(soup)
    english_description = count_english(description)

    i = 0
    for item in atr_items:
        try:
            atr_list[i] = item.text
            i += 1
        except Exception as exc:
            break
    atr_list.sort(reverse=True)
    return {
        'title': title,
        'description': description,
        'company_name': company_name,
        'english': english_description,
        'salary_min': salary[0],
        'salary_max': salary[1],
        'age': age,
        'exp_age': exp_age,
        'ref': url,
    }


async def parse_anketa(url, semaphore, total_n, i, func):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    print(resp.status, i, total_n, url)
                    try:
                        htmltext = await resp.text()
                    except Exception as exc:
                        return None
                    args = []
                    args.append(htmltext)
                    args.append(url)
                    result = await loop.run_in_executor(executor, func, *args)
                    resumes.append(result)
                    await asyncio.sleep(1)
            except Exception as error:
                print(error)


def clean_salary(soup):
    salary = soup.find_all('span', class_='resume-block__salary resume-block__title-text_salary')[0].text
    salary = salary.replace('\u2009', '')
    salary = salary.replace('\xa0', ' ')

    currency = find_currency(salary)

    result = convert_currency_to_rub(salary, currency)
    return result


def clean_position_salary(salary: str):
    salary = salary.replace('\u2009', '')
    salary = salary.replace('\xa0', ' ')
    salary = salary.replace('на руки', '')

    currency = find_currency(salary)
    start = salary[:salary.find('до')]
    end = salary[salary.find('до'):]
    start = convert_currency_to_rub(start, currency)
    end = convert_currency_to_rub(end, currency)

    return start, end


def find_currency(salary: str) -> str:
    salary = salary.upper()
    currencies = ['USD', 'EUR', 'ГРН', 'РУБ']
    for cur in currencies:
        if salary.find(cur) >= 0:
            return cur
    return currencies[-1]


def convert_currency_to_rub(salary: str, currency: str) -> int:
    value = re.findall("([0-9]{1,10})", salary)
    if len(value) == 1:
        value = value[0]
    elif len(value) > 1:
        res = ''
        for el in value:
            res += el
        value = res
    else:
        value = 0

    result = 0
    cur = Currencies()

    if currency == 'USD':
        result = int(value) * cur.usd
    elif currency == 'EUR':
        result = int(value) * cur.eur
    elif currency == 'грн':
        result = int(value) * cur.grivna
    else:
        result = int(value)
    return result


def clean_age(soup):
    try:
        age = soup.find_all(attrs={'data-qa': 'resume-personal-age'})[0].text
        result = re.findall("([0-9]{2})", age)
        if len(result) > 0:
            result = int(result[0])
        else:
            result = 0
    except Exception as exc:
        result = 0
    return result


def clean_exp_age(soup):
    try:
        age = soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[0].text
        result = age
        result = result.replace('Опыт работы', '')
        result = result.replace('лет', '.')
        result = result.replace('года', '.')
        result = result.replace('год', '.')
        result = result.replace('месяцев', '')
        result = result.replace('месяца', '')
        result = result.replace('месяц', '')
        result = result.replace('Work experience', '')
        result = result.replace('years', '.')
        result = result.replace('year', '.')
        result = result.replace('months', '')
        result = result.replace('month', '')
        result = result.replace(' ', '')
        result = result.replace(' ', '')
        result = float(result)
    except Exception as exc:
        result = 0

    return result


async def parse_resume_main(url, max_pages):
    tasks = []
    max_n = max_pages
    sem = asyncio.Semaphore(value=maxWorkers)
    for i in range(max_n):
        task = asyncio.Task(parse_search(url + str(i), sem))
        tasks.append(task)

    await asyncio.gather(*tasks)

    i = 0
    for ref in ref_list:
        task = asyncio.Task(parse_anketa(ref, sem, len(ref_list), i, anketa_processor))
        tasks.append(task)
        i += 1

    await asyncio.gather(*tasks)


async def parse_moscow_positions(url, max_pages):
    tasks = []
    max_n = max_pages
    sem = asyncio.Semaphore(value=1)
    for i in range(max_n):
        task = asyncio.Task(parse_positions(url + str(i), sem))
        tasks.append(task)

    await asyncio.gather(*tasks)

    sem = asyncio.Semaphore(value=maxWorkers)
    i = 0
    for ref in ref_list:
        task = asyncio.Task(parse_anketa(ref, sem, len(ref_list), i, position_processor))
        tasks.append(task)
        i += 1

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    # loop.run_until_complete(parse_resume_main(url_moscow, max_pages=100))
    loop.run_until_complete(parse_moscow_positions(url_moscow_vacancies, max_pages=50))
    df = DataFrame(resumes)
    df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
