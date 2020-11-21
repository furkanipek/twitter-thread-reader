import tweepy
import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


class TwitterThreadReader(object):
    def __init__(self):
        self.Auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.Auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.Auth)
        self.Tweets = []
        self.Thread = {}
    
    def ParseURL(self, URL):
        URL_Parse = URL.split('twitter.com/')[1].split('/status/')
        self.USER = self.api.get_user(URL_Parse[0])
        self.TweetID = URL_Parse[1]

    def GetThread(self):
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.by import By

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument("--headless")  

        service = Service('./chromedriver')
        service.start()
        driver = webdriver.Remote(service.service_url, desired_capabilities=chrome_options.to_capabilities())
        driver.implicitly_wait(10)
        driver.get("https://twitter.com/{user}/status/{tweet_id}".format(user=self.USER.screen_name, tweet_id=self.TweetID))
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains(self.USER.name))
            links = driver.find_elements_by_xpath('//a[contains(@href, "{}/status")]'.format(self.USER.screen_name))
            for link in links:
                self.Tweets.append(link.get_attribute('href').split('/status/')[-1])
        except:
            print("Loading took too much time!")
        driver.quit()

        return self.Tweets
    
    def CreateTread(self):
        for twt in self.Tweets:
            tweetS = self.api.get_status(id=twt, tweet_mode="extended")
            if tweetS.in_reply_to_status_id == None:
                self.Thread[tweetS.id] = {'full_text', tweetS.full_text}
            elif tweetS.in_reply_to_status_id in self.Thread.keys():
                self.Thread[tweetS.id] = {'full_text', tweetS.full_text}
            print(tweetS.id, tweetS.in_reply_to_status_id)
            print(tweetS.in_reply_to_status_id, tweetS.in_reply_to_status_id in self.Thread.keys(), self.Thread.keys())
        print(self.Thread)

    def GetFirstTweet(self):
        SearchTweet = self.TweetID
        while True:
            tweetS = self.api.get_status(id=SearchTweet)
            print(tweetS.id, tweetS.in_reply_to_status_id)
            if tweetS.in_reply_to_status_id == None:
                self.FirstTweetID = tweetS.id
                break
            else:
                SearchTweet = tweetS.in_reply_to_status_id
