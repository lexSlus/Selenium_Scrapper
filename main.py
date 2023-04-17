from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

website = 'https://www.audible.com/adblbestsellers?ref=a_search_t1_navTop_pl0cg1c0r0&pf_rd_p=8a113f1a-dc38-418d-b671' \
          '-3cca04245da5&pf_rd_r=BJGAP5KBFJFG4S8JGXKM&pageLoadId=2hAPmhyIT812ccNy&creativeId=1642b4d1-12f3' \
          '-4375-98fa' \
          '-4938afc1cedc '


class AudibleScraper:
    def __init__(self, url, driver_path='chromedriver.exe', headless=True, window_size=(1920, 1080)):
        self.url = url
        self.driver_path = driver_path
        self.headless = headless
        self.window_size = window_size

    def run(self):

        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument(f'--window-size={self.window_size[0]}x{self.window_size[1]}')

        service = Service(executable_path=self.driver_path)

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(website)
        driver.maximize_window()

        # pagination
        pagination = driver.find_element(By.XPATH, '//ul[contains(@class, "pagingElements")]')
        pages = pagination.find_elements(By.TAG_NAME, 'li')
        last_page = int(pages[-2].text)

        current_page = 1

        book_title = []
        book_author = []
        book_length = []

        while current_page <= last_page:
            time.sleep(2)
            container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'adbl-impression'
                                                                                                      '-container ')))
            # container = driver.find_element(By.CLASS_NAME, 'adbl-impression-container ')
            products = WebDriverWait(container, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//li[contains('
                                                                                                        '@class, '
                                                                                                        '"productListItem")]')))
            # products = container.find_elements(By.XPATH, '//li[contains(@class, "productListItem")]')

            for product in products:
                book_title.append(product.find_element(By.XPATH, './/h3[contains(@class, "bc-heading")]').text)
                book_author.append(product.find_element(By.XPATH, './/li[contains(@class, "authorLabel")]').text)
                book_length.append(product.find_element(By.XPATH, './/li[contains(@class, "runtimeLabel")]').text)

            current_page += 1

            try:
                next_page = driver.find_element(By.XPATH, '//span[contains(@class, "nextButton")]')
                next_page.click()
            except:
                pass

        driver.quit()

        df_books = pd.DataFrame({'title': book_title, 'author': book_author, 'length': book_length})
        df_books.to_csv('books.csv', index=False)


scraper = AudibleScraper(website)
scraper.run()
