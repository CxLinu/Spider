import random

from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib import request
from PIL import Image

import time
import csv
import pytesseract
import re


class BossSpider(object):

    driver_path = r'/usr/local/bin/chromedriver'

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=BossSpider.driver_path)
        pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.0.0_1/bin/tesseract'
        # self.urls = []
        # self.url = 'https://www.zhipin.com/job_detail/?query=python&city=100010000&industry=&position='
        self.domain = 'https://www.zhipin.com'
        fp = open('boss.csv', 'a', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(fp, ['company_name', 'position_name', 'salary', 'city', 'work_years','education',
                                          'advantage'])
        self.writer.writeheader()
        self.urls = []
        # self.positions = []

    def get_urls(self):
        with open('boss_urls.txt', 'r') as f:
            self.urls = f.read().split(',')
        # print(type(urls[2]))

    def run(self):
        self.get_urls()
        for url in self.urls:
            time.sleep(random.randint(2, 4))
            self.driver.get(url)
            while True:
            # j = 1
            # while j == 1:
                # if len(self.driver.find_element_by_id("captcha")) > 0:
                #     self.fill_captch()
                #     time.sleep(2)
                #     continue
                source = self.driver.page_source
                self.parse_list_page(source)
                WebDriverWait(self.driver, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='page']/a[@ka='page-next']"))
                )
                # time.sleep(2)
                next_btn = self.driver.find_element_by_xpath("//div[@class='page']/a[@ka='page-next']")

                if "disabled" in next_btn.get_attribute('class'):
                    break
                else:
                    time.sleep(random.randint(1, 3))
                    next_btn.click()
                time.sleep(random.randint(2, 5))
                # j = j+1
        self.driver.quit()

    def fill_captch(self):
        captchaInput = self.driver.find_element_by_id("captcha")
        captchaImage = self.driver.find_element_by_class_name("code")
        submitBtn = self.driver.find_element_by_class_name("btn")
        src = captchaImage.get_attribute("src")
        request.urlretrieve(self.domain + src, 'captcha.png')
        image = Image.open('captcha.png')
        text = pytesseract.image_to_string(image)
        captcha = re.sub(r"[\s/]", "", text)
        captchaInput.send_keys(captcha)
        submitBtn.click()

    def parse_list_page(self, source):
        html = etree.HTML(source)
        links = html.xpath("//div[@class='info-primary']//a/@href")
        for link in links:
            url = self.domain + link
            time.sleep(random.randint(2, 4))
            self.request_detail_page(url)

    def request_detail_page(self, url):

        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        source = self.driver.page_source
        try:
            self.parse_detail_page(source)
        except:
            self.fill_captch()
            self.parse_detail_page(source)
        # 关闭详情页
        time.sleep(random.randint(2, 4))
        self.driver.close()
        # 切换回职位列表页
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self, source):
        html = etree.HTML(source)
        company_name = html.xpath("//div[@class='company-info']/a/@title")[0].strip()
        position_name = html.xpath("//div[@class='name']/h1/text()")[0].strip()
        salary = html.xpath("//div[@class='name']/span[@class='salary']/text()")[0].strip()
        infos = self.driver.find_element_by_class_name("job-primary").find_element_by_tag_name("p").text
        city = infos[0:2]
        work_years = infos[2:len(infos)-2]
        education = infos[len(infos)-2:len(infos)]
        advantage = html.xpath(
            "//div[@class='tag-container']/div[@class='job-tags']/span/text()")
        advantage = ",".join(list(set(advantage)))
        # desc = html.xpath("//div[@class='job-sec']/div[@class='text']//text()")
        # desc = "/n".join(desc).strip()

        position = {
            'company_name': company_name,
            'position_name': position_name,
            'salary': salary,
            'city': city,
            'work_years': work_years,
            'education': education,
            'advantage': advantage,
            # 'desc': desc
        }
        self.write_position(position)

    def write_position(self, position):
        self.writer.writerow(position)
        print(position)


if __name__ == '__main__':
    spider = BossSpider()
    spider.run()
