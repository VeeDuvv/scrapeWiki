
# coding: utf-8

# In[2]:

from bs4 import BeautifulSoup
from urllib import request
from lxml.html import fromstring 
import re
import csv
import pandas as pd


wiki = "http://en.wikipedia.org/wiki/List_of_England_Test_cricket_records"
header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
req = request.Request(wiki,headers=header)
page = request.urlopen(req)

soup = BeautifulSoup(page, "lxml")

tables = soup.find_all('table')

for table in tables:
    tmp = table.find_all('tr')
    first = tmp[0]
    allRows = tmp[1:]
    headers = [header.get_text() for header in first.find_all('th')]
    results = [[data.get_text() for data in row.find_all('td')] for row in allRows]
    rowspan = []

    for no, tr in enumerate(allRows):
        tmp = []
        for td_no, data in enumerate(tr.find_all('td')):
            #print  (repr(tr.getText()))
            if data.has_attr("rowspan"):
                rowspan.append((no, td_no, int(data["rowspan"]), data.get_text()))
    if rowspan:
        for i in rowspan:
            # tr value of rowspan in present in 1th place in results
            for j in range(1, i[2]):
                #- Add value in next tr.
                results[i[0]+j].insert(i[1], i[3])
    df = pd.DataFrame(data=results, columns=headers)
    print (df)


# In[ ]:




# In[ ]:



