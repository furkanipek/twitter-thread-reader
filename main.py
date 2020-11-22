import tweepy
import os, re
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
        #Tweepy
        self.Auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.Auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.Auth)

        self.Tweets = []
        self.Thread = {}

        self.USER = None
        self.TweetID = None
        self.FirstTweetID = None
        
        # Query APIs minimized
        self.SearchAllTweet = {}
    
    def ParseURL(self, URL):
        TwitterUser = None
        TweetID = None
        m = re.search('(http|https)://twitter.com/(.*)/status/([0-9]*)', URL)
        if m:
            TwitterUser = m.group(2)
            TweetID = m.group(3)
        elif URL.isnumeric():
            TweetID = URL
        
        try:
            tweetS = self.api.get_status(id=TweetID, tweet_mode="extended")
            TwitterUser = tweetS.user.screen_name
            self.USER = self.api.get_user(TwitterUser)
            self.TweetID = TweetID
        except tweepy.TweepError as e:
            print("[Err {}] {}".format(e.args[0][0]['code'], e.args[0][0]['message']))

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
        driver.get("https://twitter.com/{user}/status/{tweet_id}".format(user=self.USER.screen_name, tweet_id=self.FirstTweetID))
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains(self.USER.name))
            links = driver.find_elements_by_xpath('//a[contains(@href, "{}/status")]'.format(self.USER.screen_name))
            for link in links:
                self.Tweets.append(link.get_attribute('href').split('/status/')[-1])
        except:
            print("Loading took too much time!")
        driver.quit()

        self.Tweets.sort()

        return self.Tweets
    
    def CreateTread(self):
        for twt in self.Tweets:
            if twt in self.SearchAllTweet.keys():
                self.Thread[twt] = {'full_text', self.SearchAllTweet[twt]['full_text']}
            else:    
                tweetS = self.api.get_status(id=twt, tweet_mode="extended")
                if tweetS.in_reply_to_status_id == None:
                    self.Thread[tweetS.id] = {'full_text': tweetS.full_text}
                elif tweetS.in_reply_to_status_id in self.Thread.keys():
                    self.Thread[tweetS.id] = {'full_text': tweetS.full_text}
        return self.Thread

    def GetFirstTweet(self):
        SearchTweet = self.TweetID
        while self.FirstTweetID is None:
            tweetS = self.api.get_status(id=SearchTweet, tweet_mode="extended")
            self.SearchAllTweet[tweetS.id] = tweetS._json
            if tweetS.in_reply_to_status_id == None:
                self.FirstTweetID = tweetS.id
            else:
                SearchTweet = tweetS.in_reply_to_status_id

    def ThreadRead(self, URL):
        self.ParseURL(URL)
        self.GetFirstTweet()
        self.GetThread()
        return self.CreateTread()