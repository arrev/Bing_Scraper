import string
import json
import re
import random

import requests
from bs4 import BeautifulSoup

class BingScraper():
    """
    This class handles querys to the bing search engine and returns information about the found entries.
    """
    def __init__(self,pagination=False,output_file=False):
        """
        self.pagination -> Boolean of wether we need pagination or not
        self.output_file -> Filename where the output will be stored as json. 
                            If it's not specified the result urls will be printed
        self.results -> List of dictionaries, where each dictionary is an entry in bing.
                        It includes url,title and caption.
        """

        self.pagination = pagination
        self.output_file = output_file
        self.results = []

        self.base_url = "https://www.bing.com/"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:110.0) Gecko/20100101 Firefox/110.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://www.bing.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
        }
    def scrape(self, query):
        """
        Given a query, retrieves the entries. 
        If specified, it paginates and stores the information as json
        It returns True if the query has gone well and False if there are no results.
        """

        print(f"Retrieving results for {query}")

        response = self.get_first_page(query)
        not_found = re.search(f"There are no results for\s*(?:<strong>)?{query}",response.text)
        if not_found:
            print(f"There are no results for {query}")
            return False

        self.parse_response(response.text)
        if self.pagination:
            print("Starting pagination")
            for _ in range(100): # avoid infinite loops, limit is an arbitrary number
                response = self.get_next_page(response.text)
                if response is None:
                    break
                self.parse_response(response.text)
        if self.output_file:
            self.store_output()
        else:
            output_urls = [result["url"] for result in self.results]
            print(output_urls)
        return True


    def get_first_page(self, query):
        """
        Given a query, requests the first page of entries 
        """
        query = str(query)
        # random alphnumeric string of len 32 that identifies the search result collection
        cvid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

        params = {
            'q': query,
            'form': 'QBLH', 
            'sp': '-1',

            'ghc': '1',
            'lq': '0',
            'pq': query.lower(),
            'sc': '10-1',
            'qs': 'n',
            'sk': '',
            'cvid': cvid,
            'ghsh': '0',
            'ghacc': '0',
            'ghpl': '',
        }

        response = requests.get(f'{self.base_url}search',
                                params=params,
                                headers=self.headers,
                                timeout=10)
        return response

    def get_next_page(self,response):
        """
        Given a page of responses, retrieves the next page.
        """
        soup = BeautifulSoup(response,"html.parser")
        next_page = soup.find("a",{"class":"sb_bp","title":"Next page"})
        if next_page is None:
            return None
        next_page = next_page.get("href")
        response =  requests.get(f"{self.base_url}{next_page}",
                                 headers=self.headers,
                                 timeout=10)
        return response

    def parse_response(self,response):
        """
        Parses all the entries of a page of responses.
        For each entry stores: url, title and caption.
        """
        soup = BeautifulSoup(response,"html.parser")
        results_list = soup.find("ol",{"id":"b_results"}).find_all("li",{"class":"b_algo"})
        for element in results_list:

            header = element.find("h2")
            title = header.get_text()
            href = header.find("a").get("href")
            caption = element.find("div",{"class":"b_caption"}).find("p")
            if caption is not None:
                caption = caption.get_text()

            self.results.append({"title":title,"url":href, "caption":caption})
    def store_output(self):
        """
        Stores the output as a json on the file specified in self.output_file
        """
        with open(self.output_file,"w",encoding="utf-8") as f:
            f.write(json.dumps(self.results,indent=4))

        print(f"File saved in {self.output_file}")

if __name__ == '__main__':
    #query = "enthec"
    query = 'filetype:pdf "test"'
    BingScraper(pagination=True,output_file="data/output.json").scrape(query)
