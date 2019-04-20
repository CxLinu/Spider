from selenium import webdriver
import time


class getUrls(object):

    driver_path = r'/usr/local/bin/chromedriver'

    def __init__(self, home_page):
        self.driver = webdriver.Chrome(executable_path=getUrls.driver_path)
        # 可以添加或者修改词条
        self.categories = ['Java', 'C#', 'Python', 'HTML5', 'Android', 'IOS']
        self.home_page = home_page
        self.urls = []

    def get_lagou(self):
        self.driver.get(self.home_page)
        for category in self.categories:
            self.driver.find_element_by_id('cboxClose').click()
            # 等待页面加载完成
            time.sleep(2)
            inputTag = self.driver.find_element_by_id('search_input')
            inputTag.send_keys(category)
            self.driver.find_element_by_id('search_button').click()
            # 等待页面加载完成
            time.sleep(2)
            self.urls.append(self.driver.current_url)
            # 增加延时，避免被要求登陆
            time.sleep(2)
            self.driver.back()
        self.to_save("lagou")
        self.driver.quit()

    def get_boss(self):
        self.driver.get(self.home_page)
        for category in self.categories:
            inputTag = self.driver.find_element_by_class_name('ipt-search')
            inputTag.send_keys(category)
            self.driver.find_element_by_class_name('btn-search').click()
            time.sleep(2)
            self.urls.append(self.driver.current_url.replace("101010100", "100010000"))
            time.sleep(2)
            self.driver.back()
        self.to_save("boss")
        self.driver.quit()

    def to_save(self,name):
        urls = ",".join(self.urls)
        f = open('%s_urls.txt' % name , 'w')
        f.write(urls)
        f.close()


if __name__ == '__main__':
    lagou_home_page = 'https://www.lagou.com/'
    boss_home_page = 'https://www.zhipin.com/'
    get_lagou_url = getUrls(lagou_home_page)
    get_lagou_url.get_lagou()
    time.sleep(2)
    get_boss_url = getUrls(boss_home_page)
    get_boss_url.get_boss()
