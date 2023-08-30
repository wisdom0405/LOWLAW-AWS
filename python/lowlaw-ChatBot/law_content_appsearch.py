import streamlit as st
from elastic_app_search import Client
import datetime  # datetime 모듈을 추가

# Create App Search client
client = Client(
    base_endpoint="lowlaw.ent.ap-northeast-2.aws.elastic-cloud.com/api/as/v1",
    api_key="private-egnzqo7tt7fd6fngz13mmox9",
    use_https=True
)
engine_name_1 = 'law-index'
engine_name_2 = 'prec-content'

# Streamlit 애플리케이션 시작
st.title("LOWLAW :mag_right: 검색엔진")

# 사용자로부터 검색어 입력 받기
search_query = st.text_input(label="", placeholder="검색어를 입력하세요.")

# 검색 버튼 클릭 시 동작
if st.button("검색"):
    # 검색 옵션 설정 (score 점수 내림차순 정렬, 상위 3개 결과)
    search_options = {
        "sort": [{"_score": "desc"}],  # score 점수 내림차순 정렬
        "page": {"size": 3, "current": 1}  # 상위 3개 결과
    }

    # Search on Engine 1
    search_result_engine_1 = client.search(engine_name_1, search_query, search_options)

    # Search on Engine 2
    search_result_engine_2 = client.search(engine_name_2, search_query, search_options)

    # Display results for Engine 1
    st.subheader("법령 :book:")
    for result in search_result_engine_1['results']:
        score = result['_meta']['score']
        
        # 필요한 필드들을 함께 출력
        fields_to_print = ['law', 'jo', 'jo_content', 'hang', 'hang_content', 'mok', 'mok_content']
        for field in fields_to_print:
            if field in result:
                field_value = result[field]['raw']
                st.write(f"{field.capitalize()}: {field_value}")
        
        st.write(f"Score: {score}")
        st.write("-" * 40)

    # Display results for Engine 2
    st.subheader("판례 :scales:")
    for result in search_result_engine_2['results']:
        score = result['_meta']['score']
        
        # 필요한 필드들을 함께 출력
        fields_to_print = ['사건명', '사건번호', '선고일자', '법원명', '사건종류명', '판시사항', '판결요지', '참조조문', '참조판례', '판례내용']
        for field in fields_to_print:
            if field in result:
                field_value = result[field]['raw']
                if field == '선고일자':
                    # 선고일자를 datetime 형식으로 변환하여 원하는 포맷으로 출력
                    try:
                        date_value = datetime.datetime.strptime(str(int(field_value)), '%Y%m%d').strftime('%Y.%m.%d')
                        st.write(f"{field.capitalize()}: {date_value}")
                    except ValueError:
                        st.write(f"{field.capitalize()}: {field_value}")
                elif field == '판례내용':
                    # 판례내용은 expander로 처리
                    expander = st.expander(f"{field.capitalize()}")
                    expander.write(field_value, unsafe_allow_html=True)
                elif field == '참조조문':
                    field_value = field_value.replace('\n', '')  # <br> 태그로 줄바꿈 처리 
                    st.write(f"{field.capitalize()}:")
                    st.markdown(field_value, unsafe_allow_html=True)
                else:
                    st.write(f"{field.capitalize()}: {field_value}")
                    
        
        st.write(f"Score: {score}")
        st.write("-" * 40)
