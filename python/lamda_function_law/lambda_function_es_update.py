#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import boto3
from pathlib import Path
from elasticsearch import Elasticsearch,helpers
from elasticsearch.client import MlClient
import getpass                              
import re

def lambda_handler(event, context):
    # elastic 연결준비
    es_cloud_id = "lowlaw:YXAtbm9ydGhlYXN0LTIuYXdzLmVsYXN0aWMtY2xvdWQuY29tJDZjM2YyMDgyY2IzOTQzZjFhMGJlYjRkNjYzYmYzZWVkJGNlMDY0ZmE2MWIyYjQ3ZjQ4ODMyNjRjYWUzNWVkODFl"
    es_user = "elastic"
    es_pass = "LWkW2eILoZYZylsDDThLaCKY"
    es = Elasticsearch(
        cloud_id=es_cloud_id,
        basic_auth=(es_user, es_pass),
        timeout=30,            # 타임아웃 설정 (초 단위)
        max_retries=10,        # 최대 재시도 횟수
        retry_on_timeout=True  # 타임아웃 발생 시 재시도 여부
    )

    dynamodb = boto3.resource('dynamodb')
    table_name = 'LOWLAW_law_content'
    table = dynamodb.Table(table_name)
    dynamodb_data = []
    def scan_all_items(table_name):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    
        dynamodb_data = []
        last_evaluated_key = None
    
        while True:
            if last_evaluated_key:
                response = table.scan(ExclusiveStartKey=last_evaluated_key)
            else:
                response = table.scan()
            
            items = response.get('Items', [])
            dynamodb_data.extend(items)
        
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
        return dynamodb_data

    all_items = scan_all_items(table_name)
    
    if all_items == []:
        return

    index_name = "law_final"
    
    # Bulk 연산에 사용할 데이터 포맷 생성
    es_data_to_upload = []

    for data in all_items:
        law_value = data['law']
        # 'law' 값에 "시행령", "시행규칙"이 포함되어 있지 않을 때만 삭제 작업 수행
        if "시행령" not in law_value and "시행규칙" not in law_value:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match_phrase": {
                                    "law": {
                                        "query": law_value,
                                        "slop": 0  # 정확한 일치를 위해 slop를 0으로 설정
                                    }
                                }
                            },
                            {
                                "bool": {
                                    "must_not": [
                                        {
                                            "match": {
                                                "law": "시행령"
                                            }
                                        },
                                        {
                                            "match": {
                                                "law": "시행규칙"
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
            # 쿼리 실행하여 결과 가져오기
            search_result = es.search(index="law_test", body=query, size=10000)  # 최대 10000개의 문서 가져오기

            # 검색 결과에서 삭제 작업에 필요한 정보 추출
            docs_to_delete = [
                {"_op_type": "delete", "_index": hit["_index"], "_id": hit["_id"]} for hit in search_result["hits"]["hits"]
            ]
            es_data_to_upload.extend(docs_to_delete)
            
        else:
            query = {
                "query": {
                    "match_phrase": {
                        "law": {
                            "query": law_value,
                            "slop": 0  # 정확한 일치를 위해 slop를 0으로 설정
                        }
                    }
                }
            }
            # 쿼리 실행하여 결과 가져오기
            search_result = es.search(index="law_test", body=query, size=10000)  # 최대 10000개의 문서 가져오기

            # 검색 결과에서 삭제 작업에 필요한 정보 추출
            docs_to_delete = [
                {"_op_type": "delete", "_index": hit["_index"], "_id": hit["_id"]} for hit in search_result["hits"]["hits"]
            ]
            es_data_to_upload.extend(docs_to_delete)
    
    # Bulk 연산으로 문서 삭제 실행
    if es_data_to_upload:
        response = helpers.bulk(es, es_data_to_upload, raise_on_error = False)

    es_data_to_upload = []
    
    # Bulk 연산으로 데이터 업로드 실행
    for data in all_items:
        es_body = {
            'law': data['law'],
            'date': data['date'],
            'jo_content': data['jo_content'],
            'hang_content': data['hang_content'],
            'ho_content': data['ho_content'],
            'mok_content': data['mok_content'],
            'jo': data['jo'],
            'hang': data['hang'],
            'ho': data['ho'],
            'mok': data['mok']
        }
        es_data_to_upload.append({
            "_op_type": "index",  # 문서 삽입 동작
            "_index": index_name,
            "_source": es_body
        })

    if es_data_to_upload:
        response = helpers.bulk(es, es_data_to_upload, raise_on_error = False)

