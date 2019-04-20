# encoding: utf-8

from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import csv
import re
import time
import random
import os
import pandas as pd


class LagouSpider(object):

    # i = 1

    driver_path = r'/usr/local/bin/chromedriver'

    # option = webdriver.ChromeOptions()
    # option.add_argument('headless')

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=LagouSpider.driver_path)
        fp = open('../data/lagou.csv', 'a', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(fp, ['company_name', 'position_name', 'salary', 'city', 'work_years', 'education', 'advantage', 'desc', 'mark'])
        file_size = os.path.getsize(r'../data/lagou.csv')
        if file_size == 0:
            self.writer.writeheader()
        self.urls = []
        # self.url = 'https://www.lagou.com/jobs/list_php?labelWords=&fromSearch=true&suginput='
        # self.positions = []

        # self.mark = 0  # 按获取地址的顺序递增

        self.mark = 6  # java C# 爬过了 注意删除

    def get_urls(self):
        with open('lagou_urls.txt', 'r') as f:
            self.urls = f.read().split(',')
        # print(type(urls[2]))

    def run(self):
        self.get_urls()
        for url in self.urls:
            time.sleep(random.randint(2, 4))
            self.driver.get(url)
            # j = 1
            # while j >= 20:
            while True:
                WebDriverWait(driver=self.driver, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='pager_container']/span[last()]"))
                )
                source = self.driver.page_source
                self.parse_list_page(source)
                next_btn = self.driver.find_element_by_xpath("//div[@class='pager_container']/span[last()]")
                if "pager_next_disabled" in next_btn.get_attribute("class"):
                    break
                else:
                    time.sleep(random.randint(2, 4))
                    next_btn.click()
                time.sleep(random.randint(4, 6))
                # j = j + 1
            self.mark = self.mark + 1
        self.driver.quit()

    def parse_list_page(self, source):
        html = etree.HTML(source)
        links = html.xpath("//a[@class='position_link']/@href")
        for link in links:
            # print(link)
            time.sleep(random.randint(3, 4))
            self.request_detail_page(link)

    def request_detail_page(self, url):
        # self.driver.get(url)
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='job-name']/span[@class='name']"))
        )
        source = self.driver.page_source
        self.parse_detail_page(source)
        #关闭详情页
        time.sleep(random.randint(2, 4))
        self.driver.close()
        #切换回职位列表页
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self, source):
        html = etree.HTML(source)
        position_name = html.xpath("//span[@class='name']/text()")[0]
        company_name = html.xpath("//h2[@class='fl']//em/text()")[0].strip()
        job_request_spans = html.xpath("//dd[@class='job_request']//span")
        salary = job_request_spans[0].xpath('.//text()')[0].strip()
        city = job_request_spans[1].xpath('.//text()')[0].strip()
        city = re.sub(r"[\s/]", "", city)
        work_years = job_request_spans[2].xpath('.//text()')[0].strip()
        work_years = re.sub(r"[\s/]", "", work_years).replace("经验", "")
        education = job_request_spans[3].xpath('.//text()')[0].strip()
        education = re.sub(r"[\s/]", "", education)
        if "及以上" in education:
            education = education.replace("及以上", "")
        advantage = "".join(html.xpath("//dd[@class='job-advantage']//p/text()")).strip()
        advantage = ",".join(re.split(",|。|，| |、|；", advantage)).strip(',')
        # desc = "".join(html.xpath("//dd[@class='job_bt']//div[@class='job-detail']//text()"))
        # desc = "".join(desc.split())
        desc = self.driver.current_url
        position = {
            'company_name': company_name,
            'position_name': position_name,
            'salary': salary,
            'city': city,
            'work_years': work_years,
            'education': education,
            'advantage': advantage,
            'desc': desc,
            'mark': self.mark
        }
        self.write_position(position)

    # def file_do(position_info):
    #     if os.path.exists(r'/Users/caiqi/Desktop/Recruitment/lagou_data.csv') is False:
    #         open(r'/Users/caiqi/Desktop/Recruitment/lagou_data.csv', 'w').close()
    #
    #     # 获取文件大小
    #     file_size = os.path.getsize(r'/Users/caiqi/Desktop/Recruitment/lagou_data.csv')
    #     # for p_info in position_info:
    #     if file_size == 0:
    #         # 表头
    #         name = ['公司', '职位', '薪资', '城市', '工作经验', '学历要求', '职位优势', '职位描述']
    #         # 建立DataFrame对象
    #         file_test = pd.DataFrame(columns=name, data=position_info)
    #         # 数据写入
    #         file_test.to_csv(r'/Users/caiqi/Desktop/Recruitment/lagou_data.csv', encoding='utf_8_sig', index=False)
    #     else:
    #         with open(r'/Users/caiqi/Desktop/Recruitment/lagou_data.csv', 'a+', newline="") as file_test:
    #             # 追加到文件后面
    #             writer = csv.writer(file_test)
    #             # 写入文件
    #             writer.writerows(position_info)
    #
    # def to_save(self):
    #
    #     position_info = []
    #
    #     for position in self.positions:
    #
    #         company_name = position['company_name']
    #         position_name = position['position_name']
    #         salary = position['salary']
    #         city = position['city']
    #         work_years = position['work_years']
    #         education = position['education']
    #         advantage = position['advantage']
    #         desc = position['desc']
    #         position_one = [company_name, position_name, salary, city, work_years, education, advantage, desc]
    #         position_info.append(position_one)
    #         # print(position_one)
    #     LagouSpider.file_do(position_info)
    #     # print(position_info)

    def write_position(self, position):
        self.writer.writerow(position)
        print(position)


if __name__ == '__main__':
    spider = LagouSpider()
    spider.run()
