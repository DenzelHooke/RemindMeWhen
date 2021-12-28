The port that scrapyd uses must be set manually to 8080.
This can be done by bashing into the scraper container, creating a folder in etc like such:
    /etc/scrapyd/
Inside of scrapyd, copy the config variables from scrapyd's docs and paste them this scrapyd.conf file. 
Then set the http_port to the port that you are exposing within the docker-compose file.

example: "http_port=8080".

docker-compose:

scraper:
    ports:
        - 8080:8080


scraping hub:

I simply deployed my project to scraping hub. Don't forget to pip install itemloaders :)