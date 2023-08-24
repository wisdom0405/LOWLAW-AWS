# Elastic - Python 연동 후 ChatBot 테스트

from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch

# SentenceTransformer 모델 로드
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# Elasticsearch 클라이언트 설정
es_cloud_id = "lowlaw:YXAtbm9ydGhlYXN0LTIuYXdzLmVsYXN0aWMtY2xvdWQuY29tOjQ0MyQ2YzNmMjA4MmNiMzk0M2YxYTBiZWI0ZDY2M2JmM2VlZCRjZTA2NGZhNjFiMmI0N2Y0ODgzMjY0Y2FlMzVlZDgxZQ=="
es_username = "elastic"
es_pw = "LWkW2eILoZYZylsDDThLaCKY"

es = Elasticsearch(cloud_id=es_cloud_id, basic_auth=(es_username, es_pw))

# 검색할 문장
text = "곧 군대에 들어갈 수 있어서 영장이 나오면 바로 해지할 수 있다는 약정으로 원룸에 살고 있습니다. 만약 중간에 영장이 나와서 약정대로 계약해지를 한다면 월세를 내지 않아도 될까요?"

# 실제 question 내용  
# 중간에 영장 나올 경우를 대비해서 영장이 나오면 바로 해지할 수 있다는 약정과 함께 원룸에 세들어 살고 있습니다. 
# 이 경우 약정대로 해지를 통지하면 그 때부터는 더 이상 월세를 지불하지 않아도 되는 거죠.

# 문장벡터 계산
embeddings = model.encode([text])[0]

# Elasticsearch에서 embedding 필드 값 검색
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["question","answer","law", "prec", "embedding"]
}

response = es.search(index="legal_qa", body=query, size=1000)

# 가장 높은 코사인 유사도 값 초기화
max_cosine_similarity = -1
best_answer = ""


# 각 문서와의 코사인 유사도 비교
for hit in response["hits"]["hits"]:
    doc_embedding = hit["_source"]["embedding"]
    
    # Elasticsearch에서 가져온 'embedding' 값을 문자열에서 리스트로 변환
    doc_embedding = [float(value) for value in doc_embedding.strip("[]").split(", ")]
    
    cosine_similarity = util.pytorch_cos_sim(embeddings, [doc_embedding]).item()
    
    if cosine_similarity > max_cosine_similarity:
        max_cosine_similarity = cosine_similarity
        best_answer = hit["_source"]["answer"]
        related_law = hit["_source"].get("law", None) # 필드에 데이터가 존재하면 law 값을 가져오고 존재하지 않으면 None 반환
        related_prec = hit["_source"].get("prec", None)

print("가장 유사한 답변:", best_answer)
print("코사인 유사도:", max_cosine_similarity)

if related_law: # related_law 값이 존재하면 출력
    print("관련 법령:", related_law)

if related_prec:
    print("관련 판례:", related_prec)