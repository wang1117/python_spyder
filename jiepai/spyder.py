import json
import os
from urllib.parse import urlencode

import re
from hashlib import md5
import pymongo
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from config import *
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    '''返回请求索引页的代码详情'''

    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页出错")
        return None


def parse_page_index(html):
    '''解析索引页，获取页面url'''

    # 將 html 转换为 json 格式的数据
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def get_page_detail(url):
    '''获取详情页的代码'''

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错', url)
        return None


def parse_page_detail(html, url):
    '''解析详情页的代码，获取每张图片的 url '''

    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.text
    # 或者 title = soup.select('title')[0].get_text()
    # print(title)
    images_pattern = re.compile('gallery:(.*?)\ssiblingList:', re.S)
    result = re.search(images_pattern, html)
    if result:
        # print(result.group(1)[:-5])
        # 把结果转换为课处理的 json 格式
        data = json.loads(result.group(1)[:-5])
        if data and 'sub_images' in data.keys():
            images = [item.get('url') for item in data.get('sub_images')]
            for image in images:
                download_imgae(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }


def save_to_mongo(resutl):
    '''把结果存储到 mongodb 数据库中'''
    if db[MONGO_TABLE].insert(resutl):
        print('存储到MongoDB成功', resutl)
        return True
    return False


def download_imgae(url):
    '''解析图片url'''

    print('正在下载：', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content):
    '''保存文件'''

    file_path = '{0}\{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(offset):
    '''主函数'''

    html = get_page_index(offset, KEYWORD)
    # print(html)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            # print(result)
            if result:
                save_to_mongo(result)


if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END)]
    pool = Pool()
    pool.map(main, groups)
