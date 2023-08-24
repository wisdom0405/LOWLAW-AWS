#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import re
import json
import pandas as pd
from tqdm import tqdm
import xml.etree.ElementTree as ET
from urllib.request import urlopen

# elasticsearch cloud에 올리기 위해 ndjson으로 변환하는 함수
def convert_to_ndjson(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
            
# 리스트 불러오기
prec_list = pd.read_csv('./prec_list.csv')

total_prec = []

for i in tqdm(range(len(prec_list))):
    try:
        url = "https://www.law.go.kr"
        link = prec_list.loc[i]['판례상세링크'].replace('HTML', 'XML')  # 리스트 파일의 판례상세링크로 url 생성
        url += link
        response = urlopen(url).read()
        xmltree = ET.fromstring(response)

        prec_data = {}
        for element in xmltree.iter():     # XML의 모든 태그와 텍스트 저장
            tag = element.tag
            text = element.text.strip() if element.text else ""
            prec_data[tag] = text

        total_prec.append(prec_data)

    except:
        print(url)
        continue

# json으로 저장
with open('total_prec.json', 'w', encoding='utf-8') as json_file:
    json.dump(total_prec, json_file, ensure_ascii=False, indent=4)
    
# 빠진 판례를 저장할 리스트 생성
tmp_prec = []

# 사전에 크롤링한 판례파일 불러오기
try:
    with open('total_prec.json', 'r', encoding='utf-8') as json_file:
        total_prec = json.load(json_file)
except FileNotFoundError:
    pass

# 판례일련번호로 빠진 판례 구별해내기 위해 일련번호 불러오기
crawled_set = set(int(prec.get("판례정보일련번호")) for prec in total_prec if prec.get("판례정보일련번호"))

# 빠진 판례의 '판례상세링크'를 저장할 리스트 생성
missing_links = []

# 빠진 판례의 링크 추출
for link in prec_list['판례상세링크']:
    prec_id_match = re.search(r'ID=(\d+)', link)
    if prec_id_match:
        prec_id = int(prec_id_match.group(1))
        if prec_id not in crawled_set:
            missing_links.append(link)

# 빠진 판례 크롤링
for link in tqdm(missing_links):
    try:
        url = "https://www.law.go.kr"
        link = link.replace('HTML', 'XML')
        url += link
        response = urlopen(url).read()
        xmltree = ET.fromstring(response)

        prec_data = {}
        for element in xmltree.iter():
            tag = element.tag
            text = element.text.strip() if element.text else ""
            prec_data[tag] = text

        tmp_prec.append(prec_data)

    except:
        print(url)
        continue

# 빠진 판례 json에 저장
with open('tmp_prec.json', 'w', encoding='utf-8') as json_file:
    json.dump(tmp_prec, json_file, ensure_ascii=False, indent=4)
    
# total_prec 불러오기
try:
    with open('total_prec.json', 'r', encoding='utf-8') as json_file:
        total_prec = json.load(json_file)
except FileNotFoundError:
    total_prec = []

# tmp_prec 불러오기
try:
    with open('tmp_prec.json', 'r', encoding='utf-8') as json_file:
        tmp_prec = json.load(json_file)
except FileNotFoundError:
    tmp_prec = []

# 빠진 판례를 원래 크롤링된 판례에 추가
total_prec = total_prec + tmp_prec

# 합쳐진 파일을 json으로 저장
with open('total_prec.json', 'w', encoding='utf-8') as json_file:
    json.dump(total_prec, json_file, ensure_ascii=False, indent=4)
    
# 판례 전처리
# json 불러오기
with open('total_prec.json', 'r', encoding='utf-8') as json_file:
    total_data = json.load(json_file)

# 리스트인지 확인
if isinstance(total_data, list):
    # 전처리된 데이터 저장할 리스트 생성
    cleaned_total_data = []

    # 반복문으로 전처리
    for item in total_data:
        # html 태그 삭제
        cleaned_item_string = re.sub(r"<.*?>", "", json.dumps(item, ensure_ascii=False))
        cleaned_total_data.append(json.loads(cleaned_item_string))

    # json파일에 저장
    with open('total_prec.json', 'w', encoding='utf-8') as json_file:
        json.dump(cleaned_total_data, json_file, ensure_ascii=False, indent=4)

# ndjson으로 변환
if __name__ == "__main__":
    input_json_file = "total_prec.json"
    output_ndjson_file = "total_prec.ndjson"
    convert_to_ndjson(input_json_file, output_ndjson_file)

