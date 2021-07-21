from bs4 import BeautifulSoup
import requests
import os

index = requests.get('https://coreyms.com/')
soup = BeautifulSoup(index.text, 'lxml')

# with open("C:/Users/Denze/Projects/remindMe/remind_me_django/web_scraper/programs/web_scraper/scrapeme.html") as html_file:
#     soup = BeautifulSoup(html_file, 'lxml')

root = soup
# articles = soup.find_all('div', class_='article')



# for article in articles:
#     headline = article.h1.a.text
#     print(headline)
#     summary = article.p.text
#     print(summary)
#     print(f"\n")


# headline = article.h1.a.text
# print(headline)

# summary = article.p.text
# print(summary)

articles = soup.find_all('article', class_='post')

for article in articles:
    # headline = article.header.h2.a.text
    # print(headline)

    # date = article.header.p.time.text
    # print(date)

    # print()

    # summary = article.find('div', class_='entry-content').p.text 
    
    # print(summary)
    try:
        embeded = article.find('iframe', class_="youtube-player")['src']
        id = embeded.split('/')[4]
        id = id.split('?')[0]
        video_link = 'https://www.youtube.com/watch?v=' + id
    except Exception as e:
        video_link = None
    print()
    print(video_link)
    print("---------------------------------------------------")
    print()