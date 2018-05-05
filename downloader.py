from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as mp
import requests
import re
import json
import os

category = [] #圖片分類
mlinks = [] #分類的連結
num = 0 #category的index


# 爬取圖片的分類連結
def get_category():
    u = 'https://support.microsoft.com/app/content/api/content/asset/zh-tw/17781?iecbust=1525412926668'
    doc = requests.get(u).text
    data = json.loads(doc)
    links = data.get('links')
    for each in links:
        if each.get('articleId') != '13768':
            text = del_space(each.get('text'))

            # 將爬取到的圖片分類以及連結分別存進category和mlinks
            category.append(text)
            mlink = 'https://support.microsoft.com/zh-tw/help/'+each.get('articleId')+'/natural-wonders-wallpaper'
            mlinks.append(mlink)


# 抓圖的function
def get_pic(mset):
    # 全域變數 用作 category 的 index
    global num

    # 從mset中取出連結和圖片名稱
    url_pic = mset.get('link')
    name_pic = mset.get('name')

    # 抓圖
    pic = requests.get(url_pic)
    print('now download : ' + name_pic + ' : ' + url_pic)

    # 設定儲存路徑
    filename = 'D:\win10_bg\\' + category[num] + '\\' + name_pic + '.png'

    # 若無此folder 就自動產生
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 寫入檔案
    with open(filename, "wb") as f:
        f.write(pic.content)
        f.close()


# 消除圖片名稱中的空格
def del_space(s):
    return "".join(s.split(" "))


get_category()
for mlink in mlinks:
    data_set = []
    html_doc = requests.get(mlink)
    html_doc.encoding = 'utf-8'
    url = re.findall('"content": (.*$)', html_doc.text, re.S)
    soup = BeautifulSoup(url[0], 'html.parser')
    tmp_link = soup.find_all('a')
    tmp_name = soup.find_all('p')

    # 提出分類的ID 用作辨識
    check_num = str(mlink).split('/')[5]
    n = 0

    # 目前在抓圖時 第一組的精選和 11組的花朵會遇到問題 所以個案處理
    if check_num == '17780':
        n += 2
    elif check_num == '18828':
        n += 1

    # 將圖片名稱和下載路徑存進dictionary 並放進list
    for l in range(0, len(tmp_link), 2):
        data = {'link': tmp_link[l].get('href')[2:-2], 'name': tmp_name[l + n].text}
        data_set.append(data)

    # print(type(data_set))
    # 用多執行續下去跑
    pool = mp(4)
    pool.map(get_pic, data_set)
    pool.close()
    pool.join()

    # 每跑完一個分類 category的index就+1
    num += 1
