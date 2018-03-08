
# coding: utf-8

# In[1]:

crawled_list = []
created_headers = {}
dict_col_names = {'Pld':'Games_Played', 'W':'Games_Won', 'D': 'Games_Drew', 'L':'Games_Lost',                  'GF':'Goals_For','GA':'Goals_Against','GD':'Goal_Difference','Pts':'Total_Points'}


# In[2]:

def trimStrBy1 (str):
    return str[:len(str)-1]

def getFullName (str):
    str = str.strip().replace("\n","").replace(" ","_")
    #
    if "[" in str:
        str = str[:str.find("[")]
    if str not in dict_col_names:
        return str
    else:
        return dict_col_names[str]


# In[3]:

from bs4 import BeautifulSoup
from urllib import request
from lxml.html import fromstring 
import re
import csv
import pandas as pd

def getTableFrame(table):
    tmp = table.find_all('tr')
    first = tmp[0]
    allRows = tmp[1:]
    headers = [header.get_text() for header in first.find_all('th')]
    new_headers = []
    new_header = ''
    all_headers = ''
    for header in headers:
        new_header = getFullName(header)
        new_headers.append(new_header)
        all_headers = all_headers + new_header + ","
    all_headers = trimStrBy1(all_headers)
    
    results = [[data.get_text() for data in row.find_all('td')] for row in allRows]
    rowspan = []
    for row_no, tr in enumerate(allRows):
        tmp = []
        for col_no, data in enumerate(tr.find_all('td')):
            if data.has_attr("rowspan"):
                rowspan.append((row_no, col_no, int(data["rowspan"]), data.get_text()))
    if rowspan:
        for i in rowspan:
            for j in range(1, i[2]):
                results[i[0]+j].insert(i[1], i[3])
    df = pd.DataFrame(data=results, columns=new_headers)
    return df, all_headers
    


# In[ ]:

def insertIntoDB(league, league_year, success_count, df, all_headers):
    conn = sqlite3.connect('top5tables.sqlite')
    cur = conn.cursor()
    table_name = league + '_' + league_year + '_' + success_count
    df.to_sql(con=conn, name=table_name, if_exists='append', flavor='sqlite')
    conn.commit()


# In[ ]:

import wikipedia
from wikipedia import WikipediaPage
from lxml import html
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sqlite3
import re

all_tables = []
single_table = []
single_row = []

leagues = [' FA Premier League', ' Premier League', ' La Liga', ' Serie A', ' Bundesliga', ' Ligue 1', ' French Division 1']
years = [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,          2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
dashes = ['—','–','‐']


'1992–93 FA Premier League'
'1992–93 FA Premier League'


request_count = 0
success_count = 0
duplicate_count = 0

for year in years:
    for league in leagues:
        for dash in dashes:
            if year == 1999: league_year = str(year) + dash + '2000'
            else: league_year = str(year) + dash + str(year + 1)[2:]
            title = league_year + league
            try:
                request_count += 1
                print ("\n\nGetting page:",title)
                parsed_html = BeautifulSoup(wikipedia.page(title).html(), "lxml")
                page_title = wikipedia.page(title).title
                print (" Wikipedia Page Title:", page_title)
            except wikipedia.exceptions.PageError:
                print (" Page Error:",title)
            except:
                print (" General Exception:",title)

            if page_title not in crawled_list:
                tables = parsed_html.findAll('table', attrs={'class':'wikitable'})
                table_count = 0
                for table in tables:
                    if len([header.get_text() for header in table.find_all('tr')[0].find_all('th')]) > 0:
                        df, all_headers = getTableFrame(table)
                        print ("\n\t",all_headers)
                        table_count += 1
                    else:
                        continue
                    #insertIntoDB(league, league_year, str(table_count), df, all_headers)
                print (" Freshly crawled:",page_title)
                success_count += 1
                crawled_list.append(page_title)
            else:
                duplicate_count += 1
                print (" Already crawled:",page_title)
print ("Page Requested:", request_count)
print ("Success:", success_count)
print ("Duplicate:", duplicate_count)

