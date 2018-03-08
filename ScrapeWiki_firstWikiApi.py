
# coding: utf-8

# In[101]:

crawled_list = []
created_headers = {}
dict_col_names = {'Pld':'Games_Played', 'W':'Games_Won', 'D': 'Games_Drew', 'L':'Games_Lost',                  'GF':'Goals_For','GA':'Goals_Against','GD':'Goal_Difference','Pts':'Total_Points'}


# In[102]:

def trimStrBy1 (str):
    return str[:len(str)-1]

def getFullName (str):
    if str not in dict_col_names:
        return str
    else:
        return dict_col_names[str]


# In[103]:

def insertIntoDB(league, league_year, success_count, new_table, header, col_count):
    
    #print ("\n------")
    #print ("\t\t", new_table[0])
    #print ("\t\t", new_table[1])
    #print ("\t\t", new_table[2])
    
    conn = sqlite3.connect('top5tables.sqlite')
    cur = conn.cursor()
    list_of_tuples = []
    
    table_name = league + '_' + league_year + '_' + success_count
    
    if header not in created_headers:
        drop_sql = 'DROP TABLE IF EXISTS '+ table_name +';'
        create_sql = 'CREATE TABLE '+ table_name + ' (' + header +');'
        cur.executescript(drop_sql + create_sql)
        created_headers[header]=table_name
        #print ("\t\t", drop_sql)
        #print ("\t\t", create_sql)
    else:
        table_name = created_headers[header]

    insert_sql = 'INSERT INTO ' + table_name + ' VALUES ('
    
    col_num = 0
    
    while col_num < col_count:
        insert_sql = insert_sql + "?,"
        col_num += 1 
    insert_sql = trimStrBy1(insert_sql) + ')' 
    
    print ("\t\t", insert_sql)
    
    for row in new_table:
        list_of_tuples.append(tuple(row))
        #print ("\t\t", tuple(row))
        
    cur.executemany(insert_sql, list_of_tuples)
    conn.commit()


# In[104]:

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

leagues = ['Premier_League']#, 'La_Liga', 'Serie_A', 'Bundesliga', 'Ligue_1']
years = [1992]#, 1993], 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 
        #2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]
dashes = ['–','—']


request_count = 0
success_count = 0
duplicate_count = 0

for dash in dashes:
    for league in leagues:
        for year in years:
            
            if year == 1999: league_year = str(year) + dash + '2000'
            else: league_year = str(year) + dash + str(year + 1)[2:]

            title = league_year + '_' + league

            try:
                request_count += 1
                print ("\nGetting page:",title)
                page_html = wikipedia.page(title).html()
                page_title = wikipedia.page(title).title
                print ("\tWikipedia Page Title:", wikipedia.page(title).title)
                parsed_html = BeautifulSoup(page_html, "lxml")
            except wikipedia.exceptions.DisambiguationError:
                print ("Disambiguation Error:",title)
            except wikipedia.exceptions.HTTPTimeoutError:
                print ("HTTP Timeout Error:",title)
            except wikipedia.exceptions.PageError:
                print ("Page Error:",title)
            except wikipedia.exceptions.RedirectError:
                print ("Redirect Error:",title)
            except wikipedia.exceptions.WikipediaException:
                print ("Wikipedia Exception:",title)
            except:
                print ("General Exception:",title)

            if page_title not in crawled_list:
                tables = parsed_html.findAll('table', attrs={'class':'wikitable'})
                all_values = []
                row_num = 0
                col_num = 0
                val_count = 0
                table_count = 0
                for table in tables:
                    skip_table = len(table.findAll('td', {'rowspan'})) > 0
                    print ("\tNew Table. Skip? ", skip_table)
                    if skip_table:
                        continue
                    else:
                        sql_header = 'League Text, Year TEXT, '
                        col_names = ''
                        col_count = 0
                        row_count = 0
                        curr_th = 0
                        curr_td = 0
                        max_th = 0
                        is_Last_Parsed_Head = False
                        element_count = 1
                        for row in table.children:
                            if row.name == 'tr':
                                curr_th = len(row.findAll('th'))
                                curr_td = len(row.findAll('td'))
                                max_th = max(curr_th, max_th)

                                if max_th > 0:
                                    for child in row.children:
                                        if child.name == 'th':
                                            col_count += 1
                                            col_name = repr(child.getText().strip()).replace('\'','')
                                            if ' ' in col_name:
                                                col_name = col_name.split()[0]
                                            col_name = getFullName(col_name)
                                            sql_header = sql_header + ' ' + col_name + ' TEXT,'
                                            col_names = col_names + ' ' + col_name + ','
                                            is_Last_Parsed_Head = True
                                        elif child.name == 'td':
                                            element_count += 1
                                            all_values.append(repr(child.getText().strip()))
                                            is_Last_Parsed_Head = False
                                        else:
                                            is_Last_Parsed_Head = False
                                            continue
                                    if is_Last_Parsed_Head == False and curr_td < max_th:
                                        while curr_td < max_th:
                                            #print ("\t\tOHC:", curr_th, ", NHC:", max_th, ", OBC:", curr_td)
                                            all_values.append('---')
                                            curr_td += 1
                                    row_count += 1
                                else:
                                    #print ("\t\tTable has no headers")
                                    break

                        row_count -= 1
                        #print ("\t", row_count)

                        if col_count > 0:
                            #print ("\t\t",header)
                            for a_value in all_values:
                                #if a_value == '' or a_value.startswith('Qual')==True or a_value.startswith('Rele')==True:
                                #    continue
                                val_count += 1

                                # start of every row, add league and year
                                if val_count%col_count == 1:
                                    single_row.append(league)
                                    single_row.append(year)
                                single_row.append(a_value)
                                # if entire row is received then start a new row
                                if val_count%col_count == 0:
                                    #print ("\t\t\tAdding:", single_row)
                                    single_table.append(single_row)
                                    single_row = []

                            sql_header = trimStrBy1(sql_header)
                            col_names = trimStrBy1(col_names)
                            print ("\tInserting table with columnes:",col_names)

                            table_count += 1
                            insertIntoDB(league, league_year, str(table_count), single_table, sql_header, col_count+2)
                            single_table = []
                            all_values = []
                        
                print ("\tFreshly crawled:",page_title)
                success_count += 1
                crawled_list.append(page_title)
            else:
                duplicate_count += 1
                print ("\tAlready crawled:",page_title)
print ("Page Requested:", request_count)
print ("Success:", success_count)
print ("Duplicate:", duplicate_count)

