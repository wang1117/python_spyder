import json
import re
import requests
from requests.exceptions import RequestException
# 添加多线程
from multiprocessing import Pool


def get_one_page(url):
    '''获取网页链接'''
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    '''正则解析网页，获取数据'''
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)'
                         + '</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>'
                         + '.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # 整理输出结果,按字典形式输出
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4][4:],
            'score': item[5] + item[6]
        }
        # print(items)


def write_to_file(content):
    '''將结果保存到文件中, 并解决中文编码问题'''

    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(offset):
    '''主函数'''
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    # print(html)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    # for i in range(10):
    #     main(i * 10)
#     添加多线程
    pool=Pool()
    pool.map(main,[i*10 for i in range(10)])
