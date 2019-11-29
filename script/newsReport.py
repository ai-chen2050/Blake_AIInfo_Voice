from __future__ import unicode_literals
import requests 
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Timer
from wxpy import * 


# instance a new object
bot = Bot(cache_path=True, console_qr=True)

# myself 
myself = bot.self

def get_dict_news():
    "获取金山词霸每日一句，英文和翻译"
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url)
    content = r.json()['content']
    note = r.json()['note']
    return content, note 

def getNews():      # 获取新浪财经新闻函数
    news_list =[]
    base_url = 'http://live.sina.com.cn/zt/f/v/finance/globalnews1'
    browser = webdriver.PhantomJS()
    browser.get(base_url) 
    html = browser.page_source

    html_bs4 = BeautifulSoup(html,'lxml') 
    info_list = html_bs4.find_all('div',class_='bd_i bd_i_og bd_i_focus clearfix')

    if len(info_list) == 0:
        info_list = html_bs4.find_all('div',class_='bd_i bd_i_og clearfix')
    if len(info_list) > 3:
        info_list = info_list[:3] 

    for info in info_list:  # 获取页面中自动刷新的新闻
        n_time = info.select('p[class="bd_i_time_c"]')[0].get_text()  # 新闻时间及内容
        n_info = info.select('p[class="bd_i_txt_c"]')[0].get_text()
        data = {
            'n_time': n_time,
            'n_info': n_info
        }
        news_list.append(data)
    return news_list[::-1] # 这里倒序，这样打印时才会先打印旧新闻，后打印新新闻

def sina():
    data_list = getNews()
    res_str = ''
    for data in data_list:
        res_str += '【报道时间】 ' + data['n_time'] +'\t\t' + '\n【简报】' + data['n_info'] + '\n\n'
        
    return res_str

def send_blank_aline():
    bot.file_helper.send('')        # send blank msg for long online
    myself.send('')

def send_news(str):
    try:
        high_groups = bot.groups().search(str)
        if len(high_groups) == 0:
            print("Can't find the group: " + str)
            return
        contents = get_dict_news()
        sinaStr = sina()
        newStr = '【 每日要闻 】 \n' + sinaStr
        if((sinaStr == "") | (contents[0] == "")):
            print('scrapy content is empty string.')
            return
        high_groups[0].send('【 每日一句 】 \n' + contents[0] + '\n\n' + contents[1])
        high_groups[0].send(newStr)
        # 5 second by once
        t = Timer(86400, send_news)
        t_online = Timer(300, send_blank_aline)
    except:
        print(u"发送消息失败")

def printSina():
    print(sina())

@bot.register()
def print_others(msg):
    print(msg)

if __name__ == "__main__":
    # printSina()
    send_news('智能社会万物互联社区群')
    embed()
    