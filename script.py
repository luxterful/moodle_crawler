# %%
from selenium import webdriver
from parsel import Selector
from six.moves.urllib.parse import urljoin
import re
import requests
import os
import json


class Spider:
    LINKS = {
        "vhb": "https://kurse.vhb.org/VHBPORTAL/kursprogramm/kursprogramm.jsp",
        "ohm": "https://elearning.ohmportal.de/course/view.php?id=975",
        "methoden_analyse": "https://elearning.ohmportal.de/pluginfile.php/79252/mod_resource/content/5/Analyse_01_Gliederung.html",
        "normen": "https://elearning.ohmportal.de/pluginfile.php/79243/mod_resource/content/9/DIN_EN_ISO_9241_gliederung.html",
        "normen_fragen": "https://elearning.ohmportal.de/pluginfile.php/79244/mod_resource/content/2/DIN_EN_ISO_9241_Fragen_Uebersicht.html",
        "psychologie": "https://elearning.ohmportal.de/pluginfile.php/79253/mod_resource/content/2/Psychologie_1_Gliederung.html",
        "farbtheorie": "https://elearning.ohmportal.de/pluginfile.php/67553/mod_resource/content/6/0_Farbtheorie.html",
        "gestaltungsgrundlagen": "https://elearning.ohmportal.de/pluginfile.php/67681/mod_resource/content/12/0_Gestaltungsgrundlagen.html",
        "prototyping": "https://elearning.ohmportal.de/pluginfile.php/67507/mod_resource/content/10/0_Prototyping.html",
        "uebung_prototypinng": "https://elearning.ohmportal.de/pluginfile.php/79722/mod_resource/content/1/Uebungsaufgaben_Prototyping/001_Aufgaben_Intro.html",
        "metriken": "https://elearning.ohmportal.de/pluginfile.php/298549/mod_resource/content/6/um_gliederung.html",
        "metriken_fragen": "https://elearning.ohmportal.de/pluginfile.php/298550/mod_resource/content/1/um_Fragen_Uebersicht.html",
        "evaluation": "https://elearning.ohmportal.de/pluginfile.php/90110/mod_resource/content/3/evaluation_001_inhalte.html",
    }

    def __init__(self, selenium_driver):
        self.visited = []
        self.html = ""
        self.driver = selenium_driver
        cookies = driver.get_cookies()
        self.req_ses = requests.Session()
        for cookie in cookies:
            self.req_ses.cookies.set(cookie["name"], cookie["value"])
        print("spider initialized")

    def start(self, chapter):
        if not self.LINKS.get(chapter):
            print(f"chapter {chapter} not found")
            exit
        print(f"start spider for chapter {chapter}")
        self.current_chapter = chapter
        self.run(self.LINKS[chapter])

    def run(self, start_url):
        self.visited.append(start_url)
        self.driver.get(start_url)

        selector = Selector(text=driver.page_source)

        article = (
            re.compile(r"<[^>]*>(.*)<\/[^>]*>")
            .match(selector.css("article").get().replace("\n", ""))
            .group(1)
        )
        self.html += f"\n\n\n<hr id='{len(self.visited)}'>\n\n\n{article}"

        files = []
        files.extend(selector.css("source::attr(src)").re(".*.mp4"))
        files.extend(selector.css("video::attr(src)").re(".*.mp4"))
        files.extend(selector.css("img::attr(src)").getall())

        for file in files:
            self.save_file(
                urljoin(self.driver.current_url, file),
                f"htdocs/{self.current_chapter}/{file}",
            )

        for link in self.all_links(self.driver.page_source):
            if link not in self.visited:
                self.run(urljoin(self.driver.current_url, link))

    def all_links(self, html):
        return map(
            lambda url: urljoin(self.driver.current_url, url),
            Selector(text=html).css("nav a::attr(href)").getall(),
        )

    def save_file(self, url, path):
        response = self.req_ses.get(url)
        if response.headers.get("Content-Type") is "text/html":
            print("file response was html")
            return

        print(f"save file: {path}")
        self.mkdir(path)
        open(path, "wb").write(response.content)

    def write_html(self):
        self.mkdir(f"htdocs/{self.current_chapter}")
        with open("template.html", "r") as template:
            with open(f"htdocs/{self.current_chapter}/index.html", "w") as output:
                output.write(
                    template.read().format(title=self.current_chapter, html=self.html)
                )

    def mkdir(self, path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise


def crawl(chapter, selenium_driver):
    spider = Spider(selenium_driver)
    spider.start(chapter)
    spider.write_html()


def save_cookies(driver):
    with open("cookies.json", "w") as f:
        json.dump(driver.get_cookies(), f)


def load_cookies(driver):
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.delete_all_cookies()
            driver.add_cookie(cookie)


# %%
driver = webdriver.Firefox()
driver.get(Spider.LINKS["vhb"])
#%%
driver.get(Spider.LINKS["vhb"])


#%%
crawl("psychologie", driver)


# %%
driver.get(Spider.LINKS["psychologie"])

# %%
driver = webdriver.Firefox()
driver.get(Spider.LINKS["ohm"])
load_cookies(driver)
driver.get(Spider.LINKS["psychologie"])

# %%
