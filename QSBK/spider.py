import re
import requests
from requests.exceptions import RequestException


def get_page(page):
    '''获取网页源代码'''

    try:
        url = "https://www.qiushibaike.com/hot/page/" + str(page)
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


def parse_page(html):
    '''解析网页'''

    pattern = re.compile(
        '<div.*?article block.*?<h2>(.*?)</h2>.*?content.*?<span>(.*?)</span>.*?<!--.*?或gif.*?>' +
        '(.*?)<div class="stats".*?<span.*?number">(\d+)</i>.*?</span>.*?<a.*?>.*?number">(\d+)</i>.*?</div>',
        re.S)
    items = re.findall(pattern, html)
    for item in items:
        # print(item[0].split(),item[1].split(),item[2].split(),item[3].split(),item[4].split())
        # print(item)
        if not item[2].split():
            print(item[0], item[1], "好笑值：" + item[3], "评论数：" + item[4])


def main(page):
    html = get_page(page)
    if html:
        # print(html)
        parse_page(html)
    else:
        print('请求网页失败！')


if __name__ == '__main__':
    for i in range(1,14):
        main(i)