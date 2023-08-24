#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pandas as pd
import xml.etree.ElementTree as ET                     
from urllib.request import urlopen                      
from tqdm import tqdm                                  
               

id = 'jinkyu2jinkyu'  

url = f'http://www.law.go.kr/DRF/lawSearch.do?OC={id}&target=prec&type=XML'
response = urlopen(url).read()
xmltree = ET.fromstring(response) 
totalCnt = int(xmltree.find('totalCnt').text)  # api의 변수 'totalCnt'를 이용하여 페이지를 나눠서 진행 

page = 1
rows = []

for i in tqdm(range(int(totalCnt / 20)+1)):
    for node in xmltree:
        try:
            판례일련번호 = node.find('판례일련번호').text
            사건명 = node.find('사건명').text
            사건번호 = node.find('사건번호').text
            선고일자 = node.find('선고일자').text
            법원명 = node.find('법원명').text
            법원종류코드 = node.find('법원종류코드').text
            사건종류명 = node.find('사건종류명').text
            사건종류코드 = node.find('사건종류코드').text
            판결유형 = node.find('판결유형').text
            선고 = node.find('선고').text
            판례상세링크 = node.find('판례상세링크').text

            rows.append({'판례일련번호': 판례일련번호,
                        '사건명': 사건명,
                        '사건번호': 사건번호,
                        '선고일자': 선고일자,
                        '법원명': 법원명,
                        '법원종류코드' : 법원종류코드,
                        '사건종류명': 사건종류명,
                        '사건종류코드': 사건종류코드,
                        '판결유형': 판결유형,
                        '선고': 선고,
                        '판례상세링크': 판례상세링크})
        except:
            continue
    page += 1
    url = f'http://www.law.go.kr/DRF/lawSearch.do?OC={id}&target=prec&type=XML&page={page}'
    response = urlopen(url).read()
    xmltree = ET.fromstring(response)

prec_list = pd.DataFrame(rows)
prec_list.to_csv('./prec_list.csv', sep=',', na_rep='NaN', encoding='utf-8', index=False)

