from bs4 import BeautifulSoup

class Row():
    def __init__(self):
        self.cols = 0

        # Attributes
        self.date = ''
        self.id = ''
        self.type = ''
        self.report = ''
        self.beat = ""
        self.location = ''

class Table(Row):
    def __init__(self):
        #Row.__init__(self)
        self.int_rows = 0
        self.int_columns = 0
        self.table_soup = None
        self.lst_rows = []
        #self.dict_atts = {'date':'', 'id':'', 'type':'', 'report':'', 'location',''}
    
    def set_cols(self):
        pass
    
    def set_atts(self):

        #TODO[]: Strip out commas before assigning to row attribute, replace comma with alternative character

        for tr in self.table_soup.children:
            if tr != '\n':
                list_data = tr.contents
                list_data = list_data[1::]
                row = Row()
                row.date = list_data[0].contents[0].replace(",",";")
                row.id = list_data[1].contents[0].replace(",",";")
                row.type = list_data[2].contents[0].replace(",",";")
                row.report = list_data[3].contents[0].replace(",",";")
                row.beat = list_data[4] .contents[0].replace(",",";")
                row.location = list_data[5].contents[0].replace(",",";")
                self.lst_rows.append(row)
                self.int_rows+=1

class Page(Table):
    def __init__(self, html, url):
        Table.__init__(self)
        self.int_number = 0
        self.str_url = ""
        self.nav_links = ""
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser') 
        self.page_count = 0
    
    def eat_soup(self):
        # make soup for the table and data only
        # remove header and navigation footer in table
        self.table_soup = self.soup.find("tbody")
        self.table_soup.contents[0].decompose()
        self.table_soup.contents[-2].decompose()

        # set the attributes
        self.set_atts()
