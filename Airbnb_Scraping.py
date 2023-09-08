import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Use filters of Airbnb!
Title = []                          
Location = []             
Description = []   
Price = []             
Interior = []                        
Ratings = []               
Reviews = []               
Features = []             
Amenities = []               

fileobj = open("input.txt")
city = []
for line in fileobj:
    city.append(line.strip())

pages = []

for i in city:
    url = i
    r = requests.get(url)
    soup = BeautifulSoup(r.text.strip(), "lxml")

    for m in range(15):
        if(m==0):
            insider = soup.find_all("a", class_="l1j9v1wn bn2bl2p dir dir-ltr")
            for purse in insider:
                link = purse.attrs['href']
                complete_link1 = "https://www.airbnb.co.in/"+link
                pages.append(complete_link1)
        else:
            next_page = soup.find("a", class_="_1bfat5l l1j9v1wn dir dir-ltr").get("href")
            complete_link = "https://www.airbnb.co.in/"+next_page

            url = complete_link
            r = requests.get(url)
            soup = BeautifulSoup(r.text.strip(), "lxml")

            insider = soup.find_all("a", class_="l1j9v1wn bn2bl2p dir dir-ltr")
            for purse in insider:
                link = purse.attrs['href']
                complete_link1 = "https://www.airbnb.co.in/"+link
                pages.append(complete_link1)


capabilities = DesiredCapabilities.CHROME.copy()
capabilities['pageLoadStrategy'] = 'none'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--log-level=3')
# set the log level 3('severe') to suppress the unnecessary log messages in the console of output in terminal

chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-setuid-sandbox')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-features=NetworkService')

for z in pages:
    time.sleep(2)
    try:
        url = z
        driver = webdriver.Chrome(desired_capabilities=capabilities, options=chrome_options)
        driver.set_page_load_timeout(600)

        try:
            driver.get(url)
        except WebDriverException as e:
            if 'ERR_NAME_NOT_RESOLVED' in str(e):
                print('Error: DNS lookup failed for URL')
                time.sleep(10)
                try:
                    driver.get(url)
                except:
                    continue
            elif 'ERR_CONNECTION_TIMED_OUT' in str(e):
                print('Error: Connection timed out')
                time.sleep(1800)
                try:
                    driver.get(url)
                except:
                    continue
            else:
                continue

        time.sleep(8)

        try:
            content = driver.page_source.encode('utf-8').strip()
        except TimeoutException:
            try:
                driver.refresh()
                time.sleep(10)
                content = driver.page_source.encode('utf-8').strip()
            except:
                continue

        soup1 = BeautifulSoup(content, "html.parser")

        try:
            title = soup1.find("h2", class_="_14i3z6h").text
            Title.append(title)
        except:
            title = "none"
            Title.append(title)

        try:
            location = soup1.find("span", class_="_9xiloll").text
            Location.append(location)
        except:
            location = "none"
            Location.append(location)

        try:
            desc = soup1.find("h1", class_="_fecoyn4").text
            Description.append(desc)
        except:
            desc = "none"
            Description.append(desc)

        try:
            price = soup1.find("span", class_="_tyxjp1").text
            n = len(str(price))
            price = str(price[1:n-1])
            Price.append(price)
        except:
            try:
                price = soup1.find("span", class_="_1y74zjx").text
                n = len(str(price))
                price = str(price[1:n-1])
            except:   
                price = "none"
            Price.append(price)

        try:
            interior = soup1.find("ol", class_="lgx66tx dir dir-ltr").text
            q = str(interior)
            x1 = q.split("·")
            try:
                x = soup1.find("div", class_="_4zdnhq").text
            except:
                x = x1[4]
            var1 = ", ".join([x1[0].strip(),x1[2].strip(),x.strip(),x1[6].strip()])
            Interior.append(var1)
        except:
            interior = "none"
            Interior.append(interior)

        try:
            amenities = soup1.find("button", class_="l1j9v1wn b65jmrv v7aged4 dir dir-ltr").text
            m = str(amenities)
            x1 = m.split(" ")
            x2 = x1[2]
            f = soup1.find_all("div", class_="_19xnuo97")    
            x3 = []
            var1 = ""
            for q in f:
                x3.append(q.text)
            for p in range(len(x3)):
                s = x3[p].find("Unavailable:")
                if(s>=0): continue
                if(p==0):
                    var1 = var1 + x3[p]
                else:
                    var1 = var1 + ", " + x3[p]
            var2 = str(var1) + " and {} more.".format(x2)
            Amenities.append(var2)
        except:
            amenities = "none"
            x3 = []
            var1 = ""
            try:
                f = soup1.find_all("div", class_="_19xnuo97")
                for q in f:
                    x3.append(q.text)
                for p in range(len(x3)):
                    s = x3[p].find("Unavailable:")
                    if(s>=0): continue
                    if(p==0):
                        var1 = var1 + x3[p]
                    else:
                        var1 = var1 + ", " + x3[p]
            except:
                var1 = "none"
            Amenities.append(var1)    

        try:
            ratings = soup1.find("span", class_="_17p6nbba").text
            x = str(ratings)
            x1 = x.split(" ")
            x2 = x1[0]
            Ratings.append(x2)
        except:
            try:
                ratings = soup1.find("span", class_="_12si43g").text
                x = str(ratings)
                x1 = x.split(" ")
                x2 = x1[0]
            except:
                x2 = "New"
            Ratings.append(x2)
        
        try:
            reviews = soup1.find("span", class_="_s65ijh7").text
            r = str(reviews)
            x1 = r.split(" ")
            x2 = x1[0]
            Reviews.append(x2)
        except:
            try:
                reviews = soup1.find("span", class_="_1jlwy4xq").text
                r = str(reviews)
                x1 = r.split(" ")
                x2 = x1[0]
            except:
                x2 = "New"
            Reviews.append(x2)

        try:
            features = soup1.find_all("div", class_="_1s11ltsf")
            x3 = []
            var1 = ""
            for q in features:
                x3.append(q.text)
            for p in range(len(x3)):
                if(p==0):
                    var1 = var1 + x3[p]
                else:
                    var1 = var1 + ", " + x3[p]
            if(len(var1.strip())==0):  
                var1 = "New"
            Features.append(var1)   
        except:
            var1 = "New"
            Features.append(var1)

        driver.quit()
    
    except:
        continue

a = {"Title": Title, "Location": Location, "Description": Description, "Prices/night": Price, "Interior": Interior, "Amenities": Amenities, "Ratings": Ratings, "Reviews": Reviews, "Features": Features}
df = pd.DataFrame.from_dict(a, orient='index')
df = df.transpose()
df.to_csv("airbnb1.csv", mode='a', index=False, header=False)