#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = dynamodb.Table('LOWLAW_law_list')

    
    # url 불러오기
    id = 'jinkyu2jinkyu'
    url = f'http://www.law.go.kr/DRF/lawSearch.do?OC={id}&target=law&sort=efdes&type=XML'
    response = urlopen(url).read()
    xmltree = ET.fromstring(response)
    totalCnt = int(xmltree.find('totalCnt').text)

    # 페이지를 나눠서 크롤링
    page = 1
    rows = []
    l_num = 1 # 테이블 번호 
    while l_num <= totalCnt:
        for node in xmltree:
            try:
                법령일련번호 = node.find('법령일련번호').text
                법령명한글 = node.find('법령명한글').text
                법령약칭명 = node.find('법령약칭명').text
                법령ID = node.find('법령ID').text
                시행일자 = node.find('시행일자').text
                법령상세링크 = node.find('법령상세링크').text

                rows.append({
                            'l_num': l_num,
                            '법령일련번호': 법령일련번호,
                            '법령명한글': 법령명한글,
                            '법령약칭명': 법령약칭명,
                            '법령ID': 법령ID,
                            '시행일자': 시행일자,
                            '법령상세링크': 법령상세링크})
                l_num += 1
            except Exception as e:
                continue
            
        page += 1
        url = f'http://www.law.go.kr/DRF/lawSearch.do?OC={id}&target=law&sort=efdes&type=XML&page={page}'
        response = urlopen(url).read()
        xmltree = ET.fromstring(response)
    
    # DynamoDB에 데이터 저장
    for row in rows:
        try:
            table_name = dynamodb.Table('LOWLAW_law_list')
            # 데이터 변환 및 DynamoDB PutItem 수행
            item = {
                'l_num': row['l_num'],
                'MST': row['법령일련번호'],
                'law_name': row['법령명한글'],
                'law_name_sum': row['법령약칭명'],
                'law_ID': row['법령ID'],
                'law_date': row['시행일자'],
                'law_link': row['법령상세링크']
            }
            table_name.put_item(Item=item)
        except Exception as e:
            print(f"데이터 저장 중 에러 발생: {e}")

