#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import xml.etree.ElementTree as ET                     
from urllib.request import urlopen                      
from datetime import datetime
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'LOWLAW_law_content'  # 테이블 이름

    # 법령 리스트 DynamoDB 테이블에서 가져오기
    law_table = dynamodb.Table('LOWLAW_law_list')
    response = law_table.scan()
    law_list = pd.DataFrame(response['Items'])

    law_to_crawl = []  # 크롤링할 법령 목록을 담을 리스트

    # 오늘 날짜를 가져옴
    today = datetime.now().date()

    # 정수형 데이터로 변환
    today_ = int(today.strftime('%Y%m%d'))

    # law_list에서 현재 날짜와 같은 데이터의 인덱스를 law_to_crawl 리스트에 추가
    for i, law_data in law_list.iterrows():
        law_date = law_data['law_date']
        law_date = int(law_date.replace('-', ''))  # 문자열을 정수형으로 변환하여 비교 가능하도록 처리
        if law_date == today_:
            law_to_crawl.append(i)

    # law_to_crawl 리스트를 DataFrame으로 변환
    law_to_crawl_df = law_list.loc[law_to_crawl]
    
    # law_to_crawl 리스트가 비어있으면 종료
    if not law_to_crawl:
        print("No laws to crawl.")
        return
    
    law_name_list = []
    law_date_list = []
    law_jo_list = []
    law_hang_list = []
    law_ho_list = []
    law_mok_list = []

    def process_string(data):
        if pd.notnull(data):
            data = data.strip()
            if len(data) > 0:
                return data[0]
        return data

    def process_number(data):
        if pd.notnull(data) and len(data) > 0:
            match = re.search(r'\d+', data)
            if match:
                return match.group()
        return data

    def change_number(string):
        if pd.isna(string):
            return string
        else:
            string = string.replace('①', '1')
            string = string.replace('②', '2')
            string = string.replace('③', '3')
            string = string.replace('④', '4')
            string = string.replace('⑤', '5')
            string = string.replace('⑥', '6')
            string = string.replace('⑦', '7')
            string = string.replace('⑧', '8')
            string = string.replace('⑨', '9')
            string = string.replace('⑩', '10')
            string = string.replace('⑪', '11')
            string = string.replace('⑫', '12')
            string = string.replace('⑬', '13')
            string = string.replace('⑭', '14')
            string = string.replace('⑮', '15')
            return string
        
    # 법령 내용을 DynamoDB에 저장하는 함수
    def save_to_dynamodb(item):
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        return response
        
    for i, row in law_to_crawl_df.iterrows():
        url = "https://www.law.go.kr"
        link = row['law_link'].replace('HTML', 'XML')
        url += link
        response = urlopen(url).read()
        xmltree = ET.fromstring(response)
        law_label = xmltree.find("./기본정보")
        law_name = law_label.find("법령명_한글")
        law_date = law_label.find("시행일자")
        
        i = 1     # 조번호를 조절하기위한 변수 i
        while True:
            jo = xmltree.find("./조문/조문단위" + '[' + str(i) + ']')
            if jo is None:
                break
            joc = jo.find("조문내용")   # joc : 조내용 
            if jo.find("항") is None:
                law_name_list.append(law_name.text)
                law_date_list.append(law_date.text)
                law_jo_list.append(joc.text)
                law_hang_list.append("")
                law_ho_list.append("")
                law_mok_list.append("")
            else:
                a = 1    # 항번호를 조절하기위한 변수 a
                while True:
                    hang = jo.find("항" + '[' + str(a) + ']')
                    if hang is None:
                        break
                    hangc = hang.find("항내용")   # hangc : 항내용
                    if hang.find("호") is None:
                        law_name_list.append(law_name.text)
                        law_date_list.append(law_date.text)
                        law_jo_list.append(joc.text)
                        law_hang_list.append(hangc.text if hangc is not None else "")
                        law_ho_list.append("")
                        law_mok_list.append("")
                    else:
                        h = 1    # 호번호를 조절하기위한 변수 h
                        while True:
                            ho = hang.find("호" + '[' + str(h) + ']')
                            if ho is None:
                                break                    
                            hoc = ho.find("호내용")   # hoc : 호내용                  
                            if ho.find("목") is None:
                                law_name_list.append(law_name.text)
                                law_date_list.append(law_date.text)
                                law_jo_list.append(joc.text)
                                law_hang_list.append(hangc.text if hangc is not None else "")
                                law_ho_list.append(hoc.text if hoc is not None else "")
                                law_mok_list.append("")
                            else:
                                m = 1    # 목번호를 조절하기위한 변수 m
                                while True:
                                    mok = ho.find("목" + '[' + str(m) + ']')
                                    if mok is None:
                                        break
                                    mokc = mok.find("목내용")   # mokc : 목내용
                            
                                    law_name_list.append(law_name.text)
                                    law_date_list.append(law_date.text)
                                    law_jo_list.append(joc.text)
                                    law_hang_list.append(hangc.text if hangc is not None else "")
                                    law_ho_list.append(hoc.text if hoc is not None else "")
                                    law_mok_list.append(mokc.text if mokc is not None else "")
                                    m += 1
                            h += 1
                    a += 1
            i += 1
                
    df = pd.DataFrame({'law': law_name_list, 'date': law_date_list, 'jo_content': law_jo_list, 'hang_content': law_hang_list, 'ho_content': law_ho_list, 'mok_content': law_mok_list})

    # 조번호, 항번호, 호번호, 목번호 추출 및 전처리 
    # 모든 셀 내의 \n과 \t를 삭제
    df = df.applymap(lambda x: x.replace('\n', '').replace('\t', '') if isinstance(x, str) else x)

    # 3번째 열에서 '(' 있는 경우 '(' 앞의 문자열 추출하여 'jo' 열 생성 및 값 설정 - 조번호 추출 열
    df['jo'] = df.iloc[:, 2].apply(lambda x: x.split('(')[0].strip() if isinstance(x, str) and '(' in x else '')

    # 'hang' 열 생성 (4번째 열 데이터를 그대로 사용) - 항번호 추출 열
    df['hang'] = df.iloc[:, 3].fillna('')

    # 'hang' 열 데이터 처리 적용
    df['hang'] = df['hang'].apply(process_string)

    # 'hang' 열 데이터 처리 적용
    df['hang'] = df['hang'].apply(change_number)

    # 'hang' 열 데이터 정수형으로 변환
    df['hang'] = pd.to_numeric(df['hang'], errors='coerce').fillna(0).astype(int)

    # '제\n항' 문자열 추가하여 수정
    df['hang'] = df['hang'].apply(lambda x: f'제{x}항' if x != 0 else '')

    # 'ho' 열 생성 - 호번호 추출 열
    df['ho'] = df.iloc[:, 4].fillna('')

    # 'ho' 열 데이터 처리 적용
    df['ho'] = df['ho'].apply(process_number)

    # 'ho' 열 데이터 정수형으로 변환
    df['ho'] = pd.to_numeric(df['ho'], errors='coerce').fillna(0).astype(int)

    # '제\n호' 문자열 추가하여 수정
    df['ho'] = df['ho'].apply(lambda x: f'제{x}호' if x != 0 else '')

    # 'mok' 열 생성 - 목번호 추출 열
    df['mok'] = df.iloc[:, 5].fillna('')

    # 'mok'열 데이터 처리 적용
    df['mok'] = df['mok'].apply(process_string)

    # '~목' 추가하여 수정
    df['mok'] = df['mok'].apply(lambda x: f'{x}목' if x != 0 else '')

    # 'mok'열이 '목'인 행의 'mok'열 데이터 비우기
    df.loc[df['mok'] == '목', 'mok'] = ''
    
    # 'l_id' 열 추가 및 값 할당
    df['l_id'] = range(1, len(df) + 1)
        
    # 법령 내용을 DynamoDB에 저장
    for l_id, (index, row) in enumerate(df.iterrows(), start=1):
        item = {
            'l_id': row['l_id'], 
            'law': row['law'],
            'date': row['date'],
            'jo_content': row['jo_content'],
            'hang_content': row['hang_content'],
            'ho_content': row['ho_content'],
            'mok_content': row['mok_content'],
            'jo': row['jo'],
            'hang': row['hang'],
            'ho': row['ho'],
            'mok': row['mok']
        }
        response = save_to_dynamodb(item)

