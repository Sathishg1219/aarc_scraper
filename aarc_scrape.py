import json
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import openpyxl
import os
import time
# upload_to_s3bucket('images')

def status_log(r):
    """Pass response as a parameter to this function"""
    url_log_file = 'url_log.txt'
    if not os.path.exists(os.getcwd() + '\\' + url_log_file):
        with open(url_log_file, 'w') as f:
            f.write('url, status_code\n')
    with open(url_log_file, 'a') as file:
        file.write(f'{r.url}, {r.status_code}\n')


# @retry
def get_soup(url, headers=None, pay_load=None):
    r = requests.Session().get(url, headers=headers, data=pay_load)
    # print(r.encoding)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup
    elif 499 >= r.status_code >= 400:
        print(f'client error response, status code {r.status_code} \nrefer: {r.url}')
        status_log(r)
    elif 599 >= r.status_code >= 500:
        print(f'server error response, status code {r.status_code} \nrefer: {r.url}')
        count = 1
        while count != 4:
            print('while', count)
            r = requests.Session().get(url, headers=headers)  # your request get or post
            print('status_code: ', r.status_code)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                return soup
                # print('done', count)
            else:
                print('retry ', count)
                count += 1
                # print(count * 2)
                time.sleep(count * 2)
    else:
        status_log(r)
        return None

def get_dictionary(manual_id=None, abstract_number=None, abstract_type=None, abstract_title=None,
                   url=None, authors=None, author_affiliation=None, abstract_text=None, keywords=None,
                   disclosure=None, images=None, tables=None, date=None, start_time=None, end_time=None,
                   location=None, category=None, sub_category=None, session_title=None, citation=None,
                   pdf_link=None, doi=None):
    dictionary = {

        'manual_id': manual_id,
        'abstract_number': abstract_number,
        'abstract_type': abstract_type,
        'abstract_title': abstract_title,
        'url': url,
        'authors': authors,
        'author_affiliation': author_affiliation,
        'abstract_text': abstract_text,
        'keywords': keywords,
        'disclosure': disclosure,
        'images': images,
        'tables': tables,
        'date': date,
        'start_time': start_time,
        'end_time': end_time,
        'location': location,
        'category': category,
        'sub_category': sub_category,
        'session_title': session_title,
        'citation': citation,
        'pdf_link': pdf_link,
        'doi': doi,
    }
    return dictionary

if __name__ == '__main__':
    dict_ = []
    event_id = os.path.basename(__file__).rstrip('.py')
    header = {
        'authority': 'www.aarc.org',
        'method': 'GET',
        'path': '/aarc-meetings/summer-forum-2022/day-one.php',
        'scheme': 'https',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        'Cookie': '_gcl_au=1.1.325973825.1701017145; _gid=GA1.2.1196136190.1701017145; cf_clearance=gSz.U1YBeP15MdXsSxsTBJOHhC4bdhrRB60HXIxRvkY-1701069746-0-1-68a38efb.31094711.8da36fcf-0.2.1701069746; _ga=GA1.2.1739155770.1701017145; _gat_UA-4489866-1=1; _ga_29QCBSXNCV=GS1.1.1701069745.3.1.1701069834.49.0.0',
        'Referer': 'https://www.aarc.org/aarc-meetings/summer-forum-2022/day-three.php',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    list1 = ['https://www.aarc.org/aarc-meetings/summer-forum-2022/day-one.php',
'https://www.aarc.org/aarc-meetings/summer-forum-2022/day-two.php',
'https://www.aarc.org/aarc-meetings/summer-forum-2022/day-three.php']
    for link in list1:
        soup = get_soup(link, header)
        # print(soup)
        # print()
        cont = soup.find_all('div', class_='row symposium')
        manual_id = 1
        for container in cont:
            contain = container.find('div', class_='col-xs-12')
            # print(contain)
            # print()

            abstract_title = contain.find('h3').text
            # print(abstract_title)
            # print()

            try:
                author = contain.find('p', class_='presenter').text.strip()
                # print(author)
                # print()
            except:
                author = ''

            try:
                abstract = container.find('div', class_='col-xs-12 col-sm-10 session-description').text
                print(abstract)
                print()
            except:
                abstract = ''

            dictionary = get_dictionary(url=link, manual_id=manual_id,
                                        abstract_text=abstract,
                                        authors=author, abstract_title=abstract_title)
            manual_id += 1
            dict_.append(dictionary)
            df = pd.DataFrame(dict_).drop_duplicates()
            df.to_csv(f'{event_id}.csv', index=False)

