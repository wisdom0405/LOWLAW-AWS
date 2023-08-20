from elastic_app_search import Client
import json

# Create App Search client
client = Client(
    base_endpoint="lowlaw.ent.ap-northeast-2.aws.elastic-cloud.com/api/as/v1",
    api_key="private-egnzqo7tt7fd6fngz13mmox9",
    use_https=True
)
engine_name = 'law-index'

# 사용자로부터 검색어 입력 받기
search_query = input("검색어를 입력하세요: ")

# 검색 옵션 설정 (score 점수 내림차순 정렬, 상위 5개 결과)
search_options = {
    "sort": [{"_score": "desc"}],  # score 점수 내림차순 정렬
    "page": {"size": 3, "current": 1}  # 상위 5개 결과 (페이지 크기와 현재 페이지 번호를 지정)
}

# search
search_result = client.search(engine_name, search_query, search_options)
print(json.dumps(search_result, ensure_ascii=False, indent=2))  # Unicode 문자를 그대로 출력하도록 설정

# 필요한 필드들을 함께 출력
for result in search_result['results']:
    score = result['_meta']['score']
    
    # 필요한 필드들을 함께 출력
    fields_to_print = ['law', 'jo', 'jo_content', 'hang', 'hang_content', 'mok', 'mok_content'] # 필요한 필드들 리스트
    for field in fields_to_print:
        if field in result:
            field_value = result[field]['raw']
            print(f"{field.capitalize()}: {field_value}\n")
    
    print(f"Score: {score}")
    print("-" * 40)