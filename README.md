# twitter-thread-reader
Twitter thread reader

## Requirements
| Plugin | Version | Link |
| ------ | ------ | ----- |
| tweepy | >= 3.9.0 | https://www.tweepy.org |
| python-dotenv | >= 0.15.0 | https://github.com/theskumar/python-dotenv |
| selenium | >= 3.141.0 | https://github.com/SeleniumHQ/selenium/ |
| chromedriver | >= 87.0.4280.20 | https://chromedriver.chromium.org/ |

## Example

```python
import main as TTR
test = TTR.TwitterThreadReader()

thread = test.ThreadRead('URL or Tweet ID')
for i in thread:
    print(thread[i]['full_text'])
```