# Elastic - Python 연결

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer #문장벡터 만들어주는 모델
from sklearn.metrics.pairwise import cosine_similarity #코사인 유사도
import json

es_cloud_id = ""
es_username = ""
es_pw = ""

es = Elasticsearch(cloud_id=es_cloud_id,basic_auth=(es_username,es_pw))

# 인덱스 이름
index_name = "legal_qa"

# 인덱스 존재 여부 확인
if es.indices.exists(index=index_name):
    print(f"Index '{index_name}' exists.")
else:
    print(f"Index '{index_name}' does not exist.")

# 검색 쿼리 작성
query = {
    "query": {
        "match_all": {}  # 모든 문서 검색
    },
    "size": 1  # 가져올 문서 수
}

# 인덱스에서 검색 실행
response = es.search(index=index_name, body=query)

# 검색 결과 처리
if "hits" in response and "hits" in response["hits"]:
    hits = response["hits"]["hits"]
    for hit in hits:
        formatted_result = json.dumps(hit["_source"], indent=2, ensure_ascii=False)
        print(f"Document ID: {hit['_id']}\n{formatted_result}\n")
else:
    print("No results found.")
