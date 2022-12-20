import requests, json, sys, os
import urllib.parse


clr = lambda: os.system('cls' if os.name == 'nt' else 'clear')
url = "http://eprints.polbeng.ac.id/cgi/search/archive/advanced?screen=Search&dataset=archive&documents_merge=ALL&documents=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&contributors_name_merge=ALL&contributors_name=&abstract_merge=ALL&abstract=&date=&keywords_merge=ALL&keywords=&subjects_merge=ANY&type=thesis&department=KODEPRODI58301%23RekayasaPerangkatLunak&department=KODEPRODI55401%23TeknikInformatika&department=KODEPRODI57302%23KeamananSistemInformasi&editors_name_merge=ALL&editors_name=&refereed=EITHER&publication_merge=ALL&publication=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&_action_search=Search"


class Scraper:
    def __init__(self, timeout=10) -> None:
        self.timeout = timeout
        self.url = url
        self.base_url = self.url.split("/cgi")[0]
        self.headers = {
            "connection": "keep-alive", 
            "host": "eprints.polbeng.ac.id", 
            "referer": "http://eprints.polbeng.ac.id", 
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }

    def get_json_url(self):
        resp = str(requests.get(
            self.url, 
            headers=self.headers, 
            timeout=self.timeout
        ).text).split(
            '<form method="get" accept-charset="utf-8" action="'
        )[-1].split("</form>")[0]

        url = "http://eprints.polbeng.ac.id/cgi/search/archive/advanced?output=JSON&_action_export_redir=Export&dataset=archive&screen=Search&order=-date/creators_name/title&cache={}&exp={}"
        exp = urllib.parse.quote_plus(str(resp.split('id="exp" value="')[-1].split('"')[0]))
        cache = urllib.parse.quote_plus(str(resp.split('id="cache" value="')[-1].split('"')[0]))
        return url.format(cache, exp)

    def fetch(self, preprocessing_callback):
        data = requests.get(
            self.get_json_url(), 
            headers=self.headers, 
            timeout=self.timeout
        ).json()

        return [{"text": preprocessing_callback(i["abstract"])} for i in data]
