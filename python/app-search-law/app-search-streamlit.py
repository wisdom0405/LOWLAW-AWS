import streamlit as st
from elastic_app_search import Client

# Create App Search client
client = Client(
    base_endpoint="",
    api_key="",
    use_https=True
)
engine_name = 'law-index'

# Streamlit 애플리케이션 시작
st.title("LOWLAW 법령검색 with App Search")

# 사용자로부터 검색어 입력 받기
search_query = st.text_input("법령검색")

# 검색 버튼 클릭 시 동작
if st.button("검색"):
    # 검색 옵션 설정 (score 점수 내림차순 정렬, 상위 5개 결과)
    search_options = {
        "sort": [{"_score": "desc"}],  # score 점수 내림차순 정렬
        "page": {"size": 3, "current": 1}  # 상위 3개 결과
    }

    # search
    search_result = client.search(engine_name, search_query, search_options)

    # 검색 결과 출력
    for result in search_result['results']:
        score = result['_meta']['score']
        
        # 필요한 필드들을 함께 출력
        fields_to_print = ['law', 'jo', 'jo_content', 'hang', 'hang_content', 'mok', 'mok_content']
        for field in fields_to_print:
            if field in result:
                field_value = result[field]['raw']
                st.write(f"{field.capitalize()}: {field_value}")
        
        st.write(f"Score: {score}")
        st.write("-" * 40)
