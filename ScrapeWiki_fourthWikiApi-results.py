
# coding: utf-8

# In[1]:

crawled_list = []
created_headers = {}
dict_col_names = {'Pos':'Position', 'Teamvte':'Team', 'Pld':'Games_Played', 'W':'Games_Won', 'D': 'Games_Drew', 'L':'Games_Lost',                  'GF':'Goals_For','GA':'Goals_Against','GD':'Goal_Difference','Pts':'Total_Points'}

dict_table_names = {
    'Team,Manager,Captain,Kit_manufacturer,Shirt_sponsor':'Kits',
    'Rank,Player,Club,Goals':'Top_Scorers',
    'Player,For,Against,Result,Date':'Hattricks',
    'Position,Team,Games_Played,Games_Won,Games_Drew,Games_Lost,Goals_For,Goals_Against,Goal_Difference,Total_Points,Qualification_or_relegation':'League_Table',
    'Team,Outgoing_manager,Manner_of_departure,Date_of_vacancy,Position_in_table,Incoming_manager,Date_of_appointment':'Managerial_Changes',
    'Home,Away,Final_Score':'Final_Match_Scores'
}


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
    headers = [header.get_text() for header in first.findChildren(['th', 'td'])]
    #print ("   ",first)
    
    # replace original headers with formatted ones
    # also make the header string using the new formatted headers
    lst_new_headers = []
    new_header = ''
    str_all_headers = ''
    for header in headers:
        new_header = getFullName(header)
        lst_new_headers.append(new_header)
        str_all_headers = str_all_headers + new_header + ","
    str_all_headers = trimStrBy1(str_all_headers)
    print ("   ",lst_new_headers)
    
    results = [[data.get_text() for data in row.findChildren(['th', 'td'])] for row in allRows]
    rowspan = []
    for row_no, tr in enumerate(allRows):
        tmp = []
        for col_no, data in enumerate(tr.findChildren(['th', 'td'])):
            if data.has_attr("rowspan"):
                row_span_text = data["rowspan"]
                if "{{{rows}}}" in row_span_text:
                    row_span_num = 1
                    #print ("|||",row_span_text,"|||")
                else:
                    row_span_num = int(data["rowspan"])
                rowspan.append((row_no, col_no, row_span_num, data.get_text()))
    if rowspan:
        for i in rowspan:
            for j in range(1, i[2]):
                results[i[0]+j].insert(i[1], i[3])
    try:
        if "Home ╲ Away" in str_all_headers or "Home_╲_Away" in str_all_headers:
            final_results, final_headers, str_all_headers = transformFrame(lst_new_headers, results)
        else:
            final_results = results
            final_headers = lst_new_headers
        df = pd.DataFrame(data=final_results, columns=final_headers)
        return df, str_all_headers
    except:
        print ("   ",lst_new_headers)
        print ("   ",results)  
    


# In[4]:

def transformFrame(lst_headers, results):
    lst_new_headers=['Home','Away','Final_Score']
    str_new_headers = 'Home,Away,Final_Score'
    for i in range(1, len(results)):
        new_row = []
        for j in range(1, len(results[i])-1):
            new_row.append(results[i][0])
            new_row.append(lst_headers[j])
            new_row.append(results[i][j])
        print ("\n\t\t", new_row)
        new_table.append(new_row)
    return new_table, lst_new_headers, str_new_headers
    


# In[5]:

def insertIntoDB(df, table_name):
    conn = sqlite3.connect('top5tables.sqlite')
    cur = conn.cursor()
    if all_headers in dict_table_names:
        df.to_sql(con=conn, name=table_name, if_exists='append', flavor='sqlite')
    conn.commit()


# In[6]:

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

titles = ['1992-93_FA_Premier_League']
''', 
'1993-94_FA_Premier_League', 
'1994-95_FA_Premier_League', 
'1995-96_FA_Premier_League', 
'1996-97_FA_Premier_League', 
'1997-98_FA_Premier_League', 
'1998-99_FA_Premier_League', 
'1999-2000_FA_Premier_League', 
'2000-01_FA_Premier_League', 
'2001-02_FA_Premier_League', 
'2002-03_FA_Premier_League', 
'2003-04_FA_Premier_League', 
'2004-05_FA_Premier_League', 
'2005-06_FA_Premier_League', 
'2006–07_FA_Premier_League', 
'2007-08_FA_Premier_League', 
'2008-09_FA_Premier_League', 
'2009-10_FA_Premier_League', 
'2010-11_FA_Premier_League', 
'2011-12_FA_Premier_League', 
'2012-13_FA_Premier_League', 
'2013-14_FA_Premier_League', 
'2014-15_FA_Premier_League', 
'2015–16 Premier League'
'''

request_count = 0
fetch_count = 0
duplicate_count = 0
success_count = 0

for title in titles:
    try:
        request_count += 1
        print ("\nGetting page:",title)
        parsed_html = BeautifulSoup(wikipedia.page(title=title, redirect=True).html(), "lxml")
        page_title = wikipedia.page(title).title
        if page_title not in crawled_list:
            fetch_count += 1
            tables = parsed_html.findAll("table", "wikitable")
            table_count = 0
            for table in tables:
                #print ("\n", tables[table_count])
                table_count += 1
                #print ("  ",table.find_all('tr')[0].findChildren(['th', 'td'])[0].getText())
                if len([cell.get_text() for cell in table.find_all('tr')[0].findChildren(['th', 'td'])]) > 0:
                    df, all_headers = getTableFrame(table)
                    #print ("    ",dict_table_names[all_headers])
                #if all_headers in dict_table_names and dict_table_names[all_headers] == 'League_Table':
                    #print ("    ",dict_table_names[all_headers])
                #    insertIntoDB(df, dict_table_names[all_headers])
                #    break
                #else:
                #    continue

            print ("   Completed")
            success_count += 1
            crawled_list.append(page_title)
        else:
            duplicate_count += 1
            #print ("    ",page_title)
    except wikipedia.exceptions.PageError:
        print ("    Page Error")
    #print (" ", page_title)
    #except:
        #print ("    General Exception")
print ("Requested:", request_count)
print ("Fetched:", fetch_count)
print ("Success:", success_count)
print ("Duplicate:", duplicate_count)


# In[ ]:



