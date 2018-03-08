
# coding: utf-8

# In[35]:

import json
from urllib import request
from urllib.request import urlopen
from urllib import parse
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import wikipedia

print (wikipedia.search("2014–15_Premier_League"))


apiurl = "http://en.wikipedia.org/w/api.php?"

titles = ['2014–15_Premier_League']
for title in titles:
    url = apiurl + urlencode({'prop':'revisions', 'rvprop':'content', 'action':'query', 'titles': title, 'format':'xml'})
    print ('Retrieving',url)
    response = urlopen(url).read().decode('utf8')
    print ('Retrieved',len(response),'characters')
    tree = ET.fromstring(response)
    #info = json.loads(response)
    #print (info)
    
    
    


# In[ ]:



