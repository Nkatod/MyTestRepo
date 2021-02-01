import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pandas import DataFrame
from concurrent.futures import ThreadPoolExecutor
import re

urlhh = 'https://hh.ru'
url = 'https://hh.ru/search/resume?area=1&specialization=1&salary_from=150000&salary_to=&label=only_with_salary&gender=male&age_from=&age_to=&text=Python&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=false&st=resumeSearch&page='
url_postion = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=true&enable_snippets=true&no_magic=true&only_with_salary=true&search_field=name&search_field=description&search_period=30&text=Python&page='
resumes = []
positions = []
ref_list = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.473'
}
usd = 75
eur = 90
maxWorkers = 4
executor = ThreadPoolExecutor(max_workers=maxWorkers)
loop = asyncio.get_event_loop()

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
                    ref_list.append(urlhh+href)
                    # resumes.append({
                    #     'title': item.find('a', class_='resume-search-item__name').get_text(),
                    #     'salary': clean_salary(salary),
                    #     'ref': urlhh+href
                    # })

                #print(resumes)

async def parsePositions(url, semaphore):
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
                    href = item.find('a', class_='bloko-link HH-LinkModifier').attrs['href']
                    ref_list.append(href)


def anketaProcessor(htmltext):
    soup = BeautifulSoup(htmltext, 'html.parser')
    title = soup.find_all('span', class_='resume-block__title-text')[0].text
    salary = clean_salary(soup)
    exp_age = clean_expAge(soup)
    age = clean_age(soup)
    atr_list = [''] * 10
    atr_items = soup.find_all('div', class_='bloko-tag bloko-tag_inline bloko-tag_countable')
    i = 0
    for item in atr_items:
        try:
            atr_list[i] = item.text
            i += 1
        except:
            break
    atr_list.sort(reverse=True)
    return {
        'title': title,
        'salary': salary,
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

def positionProcessor(htmltext):
    soup = BeautifulSoup(htmltext, 'html.parser')
    title = soup.find_all(attrs={'data-qa': 'vacancy-title'})[0].text
    salary = clean_PositionSalary(soup)
    exp_age = clean_expAge(soup)
    age = clean_age(soup)
    atr_list = [''] * 10
    atr_items = soup.find_all('div', class_='bloko-tag bloko-tag_inline bloko-tag_countable')
    i = 0
    for item in atr_items:
        try:
            atr_list[i] = item.text
            i += 1
        except:
            break
    atr_list.sort(reverse=True)
    return {
        'title': title,
        'salary': salary,
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


async def parse_anketa(url, semaphore, total_n, i, func):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status, i, total_n, url)
                htmltext = await resp.text()
                args = []
                args.append(htmltext)
                result = await loop.run_in_executor(executor, func, *args)
                resumes.append(result)
                await asyncio.sleep(1)

def clean_salary(soup):
    salary = soup.find_all('span', class_='resume-block__salary resume-block__title-text_salary')[0].text
    salary = salary.replace('\u2009', '')
    salary = salary.replace('\xa0', ' ')
    currency = re.findall("([A-Za-zА-Яа-я]{3})", salary)
    if len(currency) > 0:
        currency = currency[0]
    else:
        currency = ''

    value = re.findall("([0-9]{3,10})", salary)
    if len(value) > 0:
        value = value[0]
    else:
        value = 0

    result = 0
    if currency == 'USD':
        result = int(value) * usd
    elif currency == 'EUR':
        result = int(value) * eur
    else:
        result = int(value)
    return result

def clean_PositionSalary(soup):
    start = ''
    end = ''
    salary = ''
    # salary = soup.find_all('span', class_='bloko-header-2 bloko-header-2_lite')[0].text
    net = salary.find('на руки') > 0

    salary = soup.replace('\u2009', '')
    salary = salary.replace('\xa0', ' ')
    salary = salary.replace('от ', '')
    salary = salary.replace('до', '-')
    salary = salary.replace('на руки', '')



    currency = re.findall("([A-Za-zА-Яа-я]{3})", salary)
    if len(currency) > 0:
        currency = currency[0]
    else:
        currency = ''

    value = re.findall("([0-9]{3,10})", salary)
    if len(value) > 0:
        value = value[0]
    else:
        value = 0

    result = 0
    if currency == 'USD':
        result = int(value) * usd
    elif currency == 'EUR':
        result = int(value) * eur
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
    except:
        result = 0
    return result

def clean_expAge(soup):
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
    except:
        result = 0

    return result

async def main():
    tasks = []
    max_n = 80
    sem = asyncio.Semaphore(value=maxWorkers)
    for i in range(max_n):
        task = asyncio.Task(parse_search(url+str(i), sem))
        tasks.append(task)

    await asyncio.gather(*tasks)

    i = 0
    for ref in ref_list:
        task = asyncio.Task(parse_anketa(ref, sem, len(ref_list), i, anketaProcessor))
        tasks.append(task)
        i += 1

    await asyncio.gather(*tasks)

async def parseMoscowPositions():
    tasks = []
    max_n = 1
    sem = asyncio.Semaphore(value=maxWorkers)
    for i in range(max_n):
        task = asyncio.Task(parsePositions(url_postion+str(i), sem))
        tasks.append(task)

    await asyncio.gather(*tasks)

    i = 0
    for ref in ref_list:
        task = asyncio.Task(parse_anketa(ref, sem, len(ref_list), i, positionProcessor))
        tasks.append(task)
        i += 1

    await asyncio.gather(*tasks)

loop.run_until_complete(main())
# loop.run_until_complete(parseMoscowPositions())

# clean_PositionSalary('от 180 000 до 230 000 руб. на руки')
df = DataFrame(resumes)
df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
