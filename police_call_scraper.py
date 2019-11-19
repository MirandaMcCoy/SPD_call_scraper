from modules.scraper import *

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import time

class SearchRange():
    def __init__(self, start):
        self.date_time = start 

        self.obj_from_date = None 
        self.from_date = ""
        self.obj_to_date = None 
        self.to_date = "" 
        self.obj_from_time = None
        self.from_time = ""
        self.obj_to_time = None
        self.to_time = ""
        self.from_apm = ""
        self.to_apm = ""

        self.adjust_range(self.date_time)

    def str_obj_date(self, str_date):
        """Makes a string date into a dateTime object"""
        obj_date = datetime.datetime.strptime(str_date, "%m/%d/%Y %I:%M:%S %p")
        return obj_date
    
    def obj_str_date(self, obj_date):
        """Makes a dateTime object into a string"""
        str_date = datetime.datetime.strftime(obj_date, "%m/%d/%Y")
        return str_date
    
    def set_to_date(self):
        obj_to_date = self.obj_from_date + datetime.timedelta(days=30)
        return obj_to_date

    def get_last_date(self, object_list):
        return object_list[-1].date

    def round_time(self, dt=None):
        return dt - datetime.timedelta(minutes = dt.minute, seconds = dt.second)
    
    def adjust_range(self, last_date_time):

        if not isinstance(last_date_time, datetime.datetime):
            last_date_time = datetime.datetime.strptime(last_date_time, "%m/%d/%Y %I:%M:%S %p")

        self.obj_from_date = datetime.date(month = last_date_time.month, day = last_date_time.day, year = last_date_time.year)
        self.from_date = datetime.datetime.strftime(self.obj_from_date, "%m/%d/%Y") 

        self.obj_from_time = datetime.time(hour = last_date_time.hour, minute = last_date_time.minute, second = last_date_time.second)
        self.from_time = self.obj_from_time.strftime("%#I:%M")

        self.obj_to_date = self.obj_from_date + datetime.timedelta(days=30)
        self.to_date = datetime.datetime.strftime(self.obj_to_date, "%m/%d/%Y")

        self.obj_to_time = self.obj_from_time
        self.to_time = self.from_time

        self.from_apm = self.obj_from_time.strftime("%p")
        self.to_apm = self.obj_from_time.strftime("%p")

class Crawler(SearchRange):
    """Main Class
    instatiates and uses other classes
    """
    def __init__(self, base_url, search_start_date):
        SearchRange.__init__(self, search_start_date)
        self.base_url = base_url
        self.browser = webdriver.Chrome(r"C:\Users\wrh6748\SPD_call_scraper\chromedriver.exe")
        self.page_count = 0

        # Counters
        self.searches = 0
        self.pages = 0
        self.rows = 0

        # Timer
    
    def write(self, data):
        """Writes data to a flat file in CSV format"""
        with open("police_calls.csv", "a") as f:
            for row in data:
                f.write(row.id+',')
                f.write(row.date+',')
                f.write(row.type+',')
                f.write(row.report+',')
                f.write(row.beat+',')
                f.write(row.location+',\n')

    def get_page_count(self, page_soup):
        rows = page_soup.find_all("tr")
        pages = []
        for row in rows:
            if len(row.find_all("tr"))!=0:
                page_links = row.find_all("td")
                #pages = len(page_links)
                for page in page_links:
                    link = page.find_all('a')
                    if len(link) > 0:
                        pages.append(link[0].get('href'))
        self.page_count = len(pages)
        return len(pages)


    def crawl(self):
        """ Implements the program 
        Only place where selenium is implimented
        """
        #TODO[]: Rewrite file writer to only open once per search instead of opening and closing on every page
        #TODO[]: Implement an analytics class 
        #TODO[]: Implement Error handling to return data for analytics
        #TODO[]: Determine minnimum sleep time to avoid click interseption on search button click 

        from_fieldName = "tbStartDate"
        to_fieldName = "tbEndDate"
        submit_buttonName = "btnSearch"

        last_date = ""

        while True:
            # Insert Date Ranges into Search Fields and search
            self.browser.get(self.base_url)
            from_field = self.browser.find_element_by_name(from_fieldName)
            from_time_menu = self.browser.find_element_by_xpath("//select[@name='ddlStartTime']/option[text()='%s']" %self.from_time).click()
            from_apm_menu = self.browser.find_element_by_xpath("//select[@name='ddlStartapm']/option[text()='%s']" %self.from_apm).click()
            to_field = self.browser.find_element_by_name(to_fieldName)
            to_time_menu = self.browser.find_element_by_xpath("//select[@name='ddlEndTime']/option[text()='%s']" %self.to_time).click()
            to_apm_menu = self.browser.find_element_by_xpath("//select[@name='ddlEndapm']/option[text()='%s']" %self.to_apm).click()
            submit_button = self.browser.find_element_by_name(submit_buttonName)

            from_field.send_keys(self.from_date)
            to_field.send_keys(self.to_date)
            to_field.send_keys(Keys.ENTER) # clears the calender popup
            time.sleep(1) # wait to make sure the calender popup is out of the way
            submit_button.click()
            self.searches+=1

            page_number = 1
            while True:

                # Data Page
                page = Page(self.browser.page_source, self.browser.current_url)

                if page_number == 1:
                    self.get_page_count(page.soup)
                
                if self.page_count >= page_number:

                    page.eat_soup()

                    # write pages data to a file
                    self.write(page.lst_rows)
                    self.pages += 1
                    self.rows += page.int_rows
                    last_date = self.get_last_date(page.lst_rows)
                    page_number += 1

                    if self.page_count >= page_number:
                        self.browser.find_element_by_link_text(str(page_number)).click()

                else:
                    break

            self.adjust_range(self.round_time(self.str_obj_date(last_date)))
            print("Searches: {}      Pages: {}      Rows: {}".format(self.searches, self.pages, self.rows))


crawler = Crawler("https://www1.springfieldmo.gov/policecalls/Default.aspx", "6/20/2019 10:00:00 PM")
crawler.crawl()
