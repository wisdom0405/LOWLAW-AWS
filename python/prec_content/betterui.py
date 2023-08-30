import streamlit as st
from elastic_app_search import Client
import datetime

# Create App Search client
client = Client(
    base_endpoint="lowlaw.ent.ap-northeast-2.aws.elastic-cloud.com/api/as/v1",
    api_key="private-egnzqo7tt7fd6fngz13mmox9",
    use_https=True
)
engine_name_1 = 'law-content'
engine_name_2 = 'prec-content'

# Function to highlight search terms in text
def highlight_search_terms(text, terms):
    highlighted_text = text
    for term in terms:
        highlighted_text = highlighted_text.replace(term, f"<span style='background-color: yellow;'>{term}</span>")
    return highlighted_text

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
        
        # 필요한 필드들을 '법명'으로 한 번에 출력
        fields_to_print = ['law', 'jo', 'hang', 'ho', 'mok', 'jo_content', 'hang_content', 'ho_content', 'mok_content']
        field_values = [result[field]['raw'] for field in fields_to_print if field in result and field != 'jo_content' and field != 'hang_content' and field != 'ho_content' and field != 'mok_content']
        st.markdown(f"**법명:** {' '.join(field_values)}")
        
        combined_content = ""
        content_fields = ['jo_content', 'hang_content', 'ho_content', 'mok_content']
        for content_field in content_fields:
            if content_field in result:
                highlighted_content = highlight_search_terms(result[content_field]['raw'], search_query.split())
                combined_content += highlighted_content + " "
    
        if combined_content:
            st.markdown(f"**내용:** {combined_content}", unsafe_allow_html=True)
        
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
                formatted_field_name = f"**{field.capitalize()}**"  # Adding bold formatting to field name
                if not field_value:  # If field value is empty
                    continue
                if field == '선고일자':
                    # 선고일자를 datetime 형식으로 변환하여 원하는 포맷으로 출력
                    try:
                        date_value = datetime.datetime.strptime(str(int(field_value)), '%Y%m%d').strftime('%Y.%m.%d')
                        st.write(f"{formatted_field_name}: {date_value}")
                    except ValueError:
                        st.write(f"{formatted_field_name}: {field_value}")
                elif field in ['판시사항', '판결요지']:
                    # 판시사항과 판결요지가 있는 경우 출력
                    if field_value:
                        highlighted_value = highlight_search_terms(field_value, search_query.split())
                        highlighted_value = highlighted_value.replace('[', '\n\n[')  # 엔터 삽입 수정
                        st.write(f"{formatted_field_name}: {highlighted_value}", unsafe_allow_html=True)
                elif field == '판례내용':
                    # 판시사항과 판결요지 모두 없는 경우에만 판례내용 출력
                    if field_value:
                        highlighted_value = highlight_search_terms(field_value, search_query.split())
                        highlighted_value = highlighted_value.replace('【', '\n\n 【')  # 엔터 삽입 수정
                        expander = st.expander(formatted_field_name)  # Using formatted field name in expander title
                        expander.write(highlighted_value, unsafe_allow_html=True)
                elif field == '참조조문' or field == '참조판례':
                    # Display reference citations as plain text without line breaks
                    references = field_value.split('\n')
                    formatted_references = ' '.join([ref.strip() for ref in references])
                    # 슬래시 제거 코드 추가
                    formatted_references = formatted_references.replace('/', ' \n\n')
                    st.write(f"{formatted_field_name}:\n\n{formatted_references}")
                else:
                    st.write(f"{formatted_field_name}: {field_value}")
    
        st.write("-" * 40)