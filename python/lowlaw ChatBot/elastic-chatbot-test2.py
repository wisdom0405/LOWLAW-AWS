# Elastic - Python 연동 후 ChatBot 테스트2(다음으로 유사한 Q&A 3개까지 출력)

from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch
from operator import itemgetter

# SentenceTransformer 모델 로드
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# Elasticsearch 클라이언트 설정
es_cloud_id = "lowlaw:YXAtbm9ydGhlYXN0LTIuYXdzLmVsYXN0aWMtY2xvdWQuY29tOjQ0MyQ2YzNmMjA4MmNiMzk0M2YxYTBiZWI0ZDY2M2JmM2VlZCRjZTA2NGZhNjFiMmI0N2Y0ODgzMjY0Y2FlMzVlZDgxZQ=="
es_username = "elastic"
es_pw = "LWkW2eILoZYZylsDDThLaCKY"

es = Elasticsearch(cloud_id=es_cloud_id, basic_auth=(es_username, es_pw))

# 검색할 문장
text = "곧 군대에 들어갈 수 있어서 영장이 나오면 바로 해지할 수 있다는 약정으로 원룸에 살고 있습니다.만약 중간에 영장이 나와서 약정대로 계약해지를 한다면 월세를 내지 않아도 될까요?"

# 문장벡터 계산
embeddings = model.encode([text])[0]

# Elasticsearch에서 embedding 필드 값 검색
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["question","answer","embedding","law","prec"]
}

response = es.search(index="legal_qa", body=query, size=1000) # 반환할 검색 결과의 개수를 지정 (최대 1000개)

# 초기화
max_cosine_similarity = -1
best_answer = ""
related_data = []  # 유사한 답변과 관련 정보를 저장할 리스트

# 각 문서와의 코사인 유사도 비교
for hit in response["hits"]["hits"]:
    doc_embedding = hit["_source"]["embedding"]
    
    # Elasticsearch에서 가져온 'embedding' 값을 문자열에서 리스트로 변환
    doc_embedding = [float(value) for value in doc_embedding.strip("[]").split(", ")]
    
    cosine_similarity = util.pytorch_cos_sim(embeddings, [doc_embedding]).item()
    
    if cosine_similarity > max_cosine_similarity:
        max_cosine_similarity = cosine_similarity
        best_question = hit["_source"]["question"] # 가장 유사한 질문(원본질문)
        best_answer = hit["_source"]["answer"] # 가장 유사한 답변
        related_law = hit["_source"].get("law", None) # 참조법령이 있다면 law 데이터 가져오고 없다면 None 반환
        related_prec = hit["_source"].get("prec", None) # 참조판례가 있다면 prec 데이터 가져오고 없다면 None 반환
        
        # 새로운 최대값을 찾았으므로 관련 정보 리스트 초기화
        related_data = []
    
    # 유사한 답변 및 관련 정보 추가
    if len(related_data) < 3:
        related_data.append({
            "answer": hit["_source"]["answer"],
            "question": hit["_source"]["question"],
            "law": hit["_source"].get("law", None),
            "prec": hit["_source"].get("prec", None)
        })

# 결과 출력
print("가장 유사한 질문 :", best_question, "\n")
print("가장 유사한 답변 :", best_answer, "\n")

if related_law: # 가장 유사한 답변의 참조법령 있으면 출력
    print("참조법령 :", related_law,"\n")

if related_prec: # 가장 유사한 답변의 참조판례 있으면 출력
    print("참조판례 :", related_prec,"\n")


print("코사인 유사도 :", max_cosine_similarity,"\n") # 가장 유사한 질문과 사용자의 text와의 코사인 유사도
print("-" * 50,"\n") # 구분선

print("유사한 답변 및 관련 정보 :\n")
for i, data in enumerate(related_data, start=1):
    print(f"{i}. 유사한 질문 :", data["question"],"\n")
    print("   답변 :", data["answer"],"\n")
    
    if data["law"]:
        print("   참조법령:", data["law"])
    if data["prec"]:
        print("   참조판례:", data["prec"])
        
    print("-" * 50,"\n") # 구분선

