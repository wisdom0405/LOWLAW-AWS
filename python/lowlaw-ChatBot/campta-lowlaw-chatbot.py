# 이게 경희캠타 final chatbot
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch
from PIL import Image
from elastic_app_search import Client
import json
import datetime

# Elasticsearch 클라이언트 설정
es_cloud_id = "lowlaw:YXAtbm9ydGhlYXN0LTIuYXdzLmVsYXN0aWMtY2xvdWQuY29tOjQ0MyQ2YzNmMjA4MmNiMzk0M2YxYTBiZWI0ZDY2M2JmM2VlZCRjZTA2NGZhNjFiMmI0N2Y0ODgzMjY0Y2FlMzVlZDgxZQ=="
es_username = "elastic"
es_pw = "LWkW2eILoZYZylsDDThLaCKY"

es = Elasticsearch(cloud_id=es_cloud_id, basic_auth=(es_username, es_pw))

# Appsearch 클라이언트 설정
client = Client(
    base_endpoint="lowlaw.ent.ap-northeast-2.aws.elastic-cloud.com/api/as/v1",
    api_key="private-egnzqo7tt7fd6fngz13mmox9",
    use_https=True
)

# SentenceTransformer 모델 로드
@st.cache_data() # st 캐싱 (로컬캐시에 저장)
def cached_model():
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    return model

def load_image(img_file): # st 이미지 불러오기 함수
    img = Image.open(img_file)
    return img

def law_search(data):
    engine_name = 'law-content'
    # 검색 옵션 설정 (score 점수 내림차순 정렬, 상위 1개 결과)
    search_options = {
        "sort": [{"_score": "desc"}],  # score 점수 내림차순 정렬
        "page": {"size": 1, "current": 1}  # 상위 1개 결과 (페이지 크기와 현재 페이지 번호를 지정)
    }

    # 결과를 문자열로 저장
    result_string = ""
    
    # search
    search_query = data
    search_result = client.search(engine_name, search_query, search_options)

    # 필요한 필드들을 함께 저장
    for result in search_result['results']:
        score = result['_meta']['score']

        # 조항, 호, 목 필드 값이 있는 경우에만 'title' 변수 생성
        title_fields = [result[field]['raw'] for field in ['law', 'jo', 'hang', 'ho', 'mok'] if field in result and result[field]['raw']]
        if title_fields:
            title = " ".join(title_fields)
            title = f"**{title}**"
            content_fields = [result[field]['raw'] for field in ['jo_content', 'hang_content', 'ho_content', 'mok_content'] if field in result and result[field]['raw']]
            if content_fields:
                content = "\n\n".join(content_fields) + "\n"
        
        # result_string에 추가
        result_string += f"{title}\n\n"
        result_string += f"\n\n{content}\n\n"
        result_string += "-" * 40 + "\n"  # 구분선 추가
    
    return result_string

def prec_search(data):
    engine_name = 'prec-search'
    # 검색 옵션 설정 (score 점수 내림차순 정렬, 상위 1개 결과)
    search_options = {
        "sort": [{"_score": "desc"}],  # score 점수 내림차순 정렬
        "page": {"size": 1, "current": 1}  # 상위 3개 결과
    }

    # search
    search_query = data
    search_result = client.search(engine_name, search_query, search_options)

    # 결과 문자열 초기화
    result_string = ""

    # 결과 문자열 생성
    for result in search_result['results']:
        score = result['_meta']['score']
        
        # 필요한 필드들을 함께 출력
        fields_to_print = ['사건명', '사건번호', '선고일자', '법원명', '사건종류명', '판시사항', '판결요지', '참조조문', '참조판례', '판례내용']
        for field in fields_to_print:
            if field in result:
                field_value = result[field]['raw']
                formatted_field_name = f"**{field.capitalize()}**"
                if not field_value:
                    continue
                if field == '선고일자':
                    try:
                        date_value = datetime.datetime.strptime(str(int(field_value)), '%Y%m%d').strftime('%Y.%m.%d')
                        result_string += f"\n{formatted_field_name}: {date_value}\n"
                    except ValueError:
                        result_string += f"{formatted_field_name}: {field_value}\n"
                elif field in ['판시사항', '판결요지']:
                    if field_value:
                        highlighted_value = f"{field_value}"
                        result_string += f"\n{formatted_field_name}:\n\n{highlighted_value}\n\n"
                elif field == '판례내용':
                    if field_value:
                        highlighted_value = f"{field_value}"
                        result_string += f"{formatted_field_name}:\n\n{highlighted_value}\n\n"
                elif field == '참조조문' or field == '참조판례':
                    references = field_value.split('\n')
                    formatted_references = ' '.join([ref.strip() for ref in references])
                    result_string += f"{formatted_field_name}:\n\n{formatted_references}\n\n"
                else:
                    result_string += f"{formatted_field_name}: {field_value}\n"

        result_string += "-" * 40 + "\n"

    return result_string

def button_law():
    result1=law_search(law)
    st.session_state.messages.append({"role" : "assistant", "content": result1})


def button_prec() :
    result2=prec_search(prec)
    st.session_state.messages.append({"role" : "assistant", "content" : result2}) 

model = cached_model() # sentenceBERT 모델

logo_file = '../image/lowlaw.png' # 로고 이미지 파일경로
logo_img = load_image(logo_file) # 로고 이미지 가져옴

sumung_file = '../image/lowlaw_sumung.png' # 수뭉이 이미지 파일경로
sumung_img = load_image(sumung_file) # 수뭉이 이미지 가져옴

# sidebar
with st.sidebar:
    st.image(logo_img, width = 300, output_format = "PNG")
    st.title("임대차 분쟁 법률 조언 서비스")
    st.divider()
    

# Streamlit 앱 시작
st.header("LOWLAW :scales: AI 상황분석")

# ChatBot의 환영인사
with st.chat_message("assistant"):
    st.write("안녕하세요! LOWLAW에 오신 것을 환영합니다:wave:")
    st.write("내가 어떤 상황인지 파악하고 어떻게 해결할지 궁금하다면 LOWLAW와 대화하면서 해결해보세요")

# 사용자에게 문장 입력 받기
user_input = st.chat_input(placeholder = "어떤 상황인지 설명해주세요!")

# 문장벡터 계산
embeddings = model.encode([user_input])[0] if user_input is not None else None

# Elasticsearch에서 embedding 필드 값 검색
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["question","answer","law", "prec", "embedding"]
}

response = es.search(index="legal_qa", body=query, size=7000)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

butt = False
if user_input : # 사용자가 user_input를 입력하였다면
    # 사용자의 user_input chat message에 띄워주기
    max_cosine_similarity = -1
    best_answer = ""
    st.chat_message("user").markdown(user_input)

    # 사용자의 user_input을 chat history에 append
    st.session_state.messages.append({"role" : "user", "content" : user_input}) 
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

    if max_cosine_similarity > 0.7 : # max_cosine_similarity 값이 0.7 이상이면 해당 답변 출력
        # assistant의 답변 chat message에 띄워주기    
        with st.chat_message("assistant"):
            st.markdown(best_answer)
            if related_law: # 참조법령이 있다면 related_law 출력
                related_law_list = related_law.split(",")  # ','로 구분하여 리스트로 변환
                st.markdown(":red[참조법령] :female-judge:")
                for law in related_law_list: 
                    st.button(law,on_click=lambda:button_law())
            if related_prec: # 참조판례 있다면 related_prec 출력
                related_prec_list = related_prec.split(',')  # ','로 구분하여 리스트로 변환
                st.markdown(":red[참조판례] :scales:")
                for prec in related_prec_list: # 참조판례 리스트 안에 있는 내용 각각 버튼으로 출력  
                    st.button(prec,on_click = lambda:button_prec())
        st.session_state.messages.append({"role" : "assistant", "content" : best_answer}) # 가장 유사한 답변 append

    else:
        # assistant의 답변 chat message에 띄워주기 (0.7 이하일 때)
        with st.chat_message("assistant"):
            st.markdown("질문에 대한 답변을 찾을 수 없어요:cry: 상황에 대해서 정확히 입력해주세요!")
        st.session_state.messages.append({"role" : "assistant", "content" : "질문에 대한 답변을 찾을 수 없어요:cry: 상황에 대해서 정확히 입력해주세요!" }) # 가장 유사한 답변 append

    #st.session_state.messages.append({"role" : "assistant", "content" : related_law}) # 가장 유사한 답변의 참조법령 append
    #st.session_state.messages.append({"role" : "assistant", "content" : related_prec}) # 가장 유사한 답변의 참조판례 append