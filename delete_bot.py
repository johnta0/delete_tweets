import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TwitterDeleteBot:
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.driver = webdriver.Chrome()

    self.deleted_post_count = 0
    self.deleted_like_count = 0

  def login(self):
    print('Logging in...')
    self.driver.get("https://twitter.com/i/flow/login")
    WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.NAME, "text"))
    )
    self.driver.find_element(By.NAME, "text").click()
    self.driver.find_element(By.NAME, "text").send_keys(self.username)
    self.driver.find_element(
        By.XPATH,
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span'
    ).click() # 「次へ」をクリックしてパスワード入力画面へ
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    self.driver.find_element(By.NAME, "password").send_keys(self.password)
    self.driver.find_element(
        By.XPATH,
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/span/span'
    ).click() # 「ログイン」をクリック
    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="Profile"] | //a[@aria-label="プロフィール"]')))
    print('Login successful')
    return


  def delete_tweets(self):
    self.driver.get(f'https://twitter.com/{self.username}')
    # self._scroll_to_bottom()
    time.sleep(5)

    articles = self.driver.find_elements(By.TAG_NAME, 'article')

    print(len(articles))
    
    delete_count = 0
    undo_rt_count = 0

    for _ in range(len(articles)):
      time.sleep(1)
      article = self.driver.find_elements(By.TAG_NAME, 'article')[0]  # Always fetch the first article

      # scroll up to the top
      self.driver.execute_script("window.scrollTo(0, 0);")

      user_name_data = article.find_element(By.XPATH, './/div[@data-testid="User-Name"]').text
      author = user_name_data.split('\n')[1].replace('@', '')
      if author == self.username:
        # Delete post
        # ツイートのドロップダウンメニューをクリック
        tweet_dropdown = WebDriverWait(article, 5).until(EC.presence_of_element_located((By.XPATH, './/*[@data-testid="caret"]')))
        tweet_dropdown.click()

        # 削除ボタンをクリック
        delete_button = WebDriverWait(article, 5).until(EC.presence_of_element_located((By.XPATH, '//span[text()="削除"]')))
        delete_button.click()

        # 削除の確認ボタンをクリック
        confirm_button = WebDriverWait(article, 5).until(EC.presence_of_element_located((By.XPATH, '//span[text()="削除"]')))
        confirm_button.click()

        delete_count += 1

      else:
        # undo Retweet
        unretweet_button = article.find_element(By.XPATH, './/*[@data-testid="unretweet"]')
        unretweet_button.click()
        # 「ポストを取り消す」をクリック
        self.driver.find_element(By.XPATH, '//span[text()="ポストを取り消す"]').click()
        undo_rt_count += 1

    print(f'Deleted {delete_count} posts')
    print(f'Undoed Retweet {undo_rt_count} posts')


  def delete_likes(self):
    # いいね欄へ遷移
    self.driver.get(f'https://twitter.com/{self.username}/likes')
    # いいねマークを取得
    like_button = self.driver.find_element(By.XPATH, '//*[@data-testid="like"]')
    like_button.click()



  def close(self):
    self.driver.close()

  
  def _scroll_to_bottom(self):
      # Get initial scroll height
      last_height = self.driver.execute_script("return document.body.scrollHeight")

      while True:
        # Scroll down to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


if __name__ == "__main__":
  username = os.getenv('TWITTER_USERNAME')
  password = os.getenv('TWITTER_PASSWORD')

  bot = TwitterDeleteBot(username, password)
  bot.login()
  bot.delete_tweets()
  bot.close()
