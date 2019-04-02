import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import warnings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
from db import *

warnings.filterwarnings("ignore")
chrome_option = webdriver.ChromeOptions()
chrome_option.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_option)
wait = WebDriverWait(browser, 10)

base_url = 'https://list.mi.com/'
response = requests.get(base_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "lxml")
    brands = soup.select('.J_category ul li .category-list-title')[:18]
    count = 0
    for brand in brands:
        count = count + 1
        # href_ : https://www.mi.com/mi9/
        href_ = brand.attrs['href']
        # version : 小米9  name : 小米9
        version_name = brand.string
        if count == 16 or count == 17:
            href_ = 'https:' + href_
        url_response = requests.get(href_)
        url_soup = BeautifulSoup(url_response.text, "lxml")
        # 10000138.html
        res_url = ""
        if count != 13:
            re_compile = re.compile(r'\'https://m.mi.com/commodity/detail/(.+?)\'', re.S)
            search = re.search(re_compile, url_soup.text)
            res_url = search.group(1) + '.html'
        else:
            res_url = re.split("\\/+", href_)[3]
        # 手机购买页面url
        product_url = 'https://item.mi.com/product/' + res_url

        print(product_url)
        browser.get(product_url)
        wait.until(
            EC.presence_of_element_located((By.ID, 'J_sliderView'))
        )
        # 获取标签信息
        soup = BeautifulSoup(browser.page_source, 'lxml')
        storage_code = soup.select('#J_buyBox  .J_main  #J_list .J_step[data-index="0"] ul li')
        for storage in storage_code:
            try:
                storage_index = int(storage.attrs['data-index']) + 1
                storage_type = storage.attrs['data-name']
                storage_click = browser.find_element_by_xpath(
                    '//*[@id="J_list"]/div[1]/ul/li[' + str(storage_index) + ']/a/span[1]')
                ActionChains(browser).click(storage_click).perform()

                info_soup = BeautifulSoup(browser.page_source, 'lxml')
                allInfo = info_soup.select('#J_buyBox  .J_main  #J_list .J_step[data-index="1"] ul li')
                for info in allInfo:
                    try:
                        result = []
                        name_version_storage_color = info.attrs['data-name']
                        name_ram = name_version_storage_color.split('GB+')[0]
                        rom_color = name_version_storage_color.split('GB+')[1]
                        ram_rindex = name_ram.rindex(" ")
                        # 手机型号
                        name = name_ram[0:ram_rindex]
                        # 手机内存
                        # rom_color_pattern = re.compile(r'(\d+)GB')
                        # rom_size = re.search(rom_color_pattern, rom_color).group(1)
                        # rom = rom_size + 'GB'
                        rom = rom_color.strip().split(' ')[0]
                        # 手机颜色
                        # color = info.attrs['data-value']
                        rom_color_list = rom_color.strip().split(' ')
                        color = rom_color_list[len(rom_color_list) - 1]
                        # 手机价格
                        price = info.attrs['data-price'].split('元')[0]
                        # color = info.attrs['data-value']
                        index = int(info.attrs['data-index']) + 1

                        img_click = browser.find_element_by_xpath('//*[@id="J_list"]/div[2]/ul/li[' + str(index) + ']')
                        ActionChains(browser).click(img_click).perform()

                        img_soup = BeautifulSoup(browser.page_source, 'lxml')
                        base_img = img_soup.select_one('#J_sliderView img')
                        # 图片url
                        img_url = base_img.attrs['src']
                        print(
                            '小米手机' + ' ' + version_name + ' ' + version_name + ' ' + rom + ' ' + color + ' ' + price + ' ' + img_url + ' ' + product_url)
                        time.sleep(0.2)
                        result.append({
                                    "brand_name": '小米手机',
                                    "name": version_name,
                                    "version": version_name,
                                    "storage_name": rom,
                                    "color_name": color,
                                    "price": price,
                                    "img_url": img_url,
                                    "url": product_url,
                                    "app_code":"XN3"
                                })
                    except Exception:
                        pass
                save(result)
            except Exception:
                pass
    browser.quit()
else:
    print("该页面不存在")
