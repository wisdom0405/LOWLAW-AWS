# 이건 옛날 코드
import streamlit as st
from streamlit_chat import message
from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch
from PIL import Image

# Elasticsearch 클라이언트 설정
es_cloud_id = "lowlaw:YXAtbm9ydGhlYXN0LTIuYXdzLmVsYXN0aWMtY2xvdWQuY29tOjQ0MyQ2YzNmMjA4MmNiMzk0M2YxYTBiZWI0ZDY2M2JmM2VlZCRjZTA2NGZhNjFiMmI0N2Y0ODgzMjY0Y2FlMzVlZDgxZQ=="
es_username = "elastic"
es_pw = "LWkW2eILoZYZylsDDThLaCKY"

es = Elasticsearch(cloud_id=es_cloud_id, basic_auth=(es_username, es_pw))

# SentenceTransformer 모델 로드
@st.cache_data() # st 캐싱 (로컬캐시에 저장)
def cached_model():
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    return model

def load_image(img_file): # st 이미지 불러오기 함수
    img = Image.open(img_file)
    return img

model = cached_model() # sentenceBERT 모델

# Streamlit 앱 시작
logo_file = '/Users/wisdom/Documents/데이터분석/ChatBot_legalQA/lowlaw.png' #st 로고 이미지 파일경로
logo_img = load_image(logo_file) #st 이미지 load(로고이미지)
st.image(logo_img, width = 650, output_format = "PNG") #st로고 이미지 삽입
st.divider() #st구분선
st.header('AI 상황분석') #st 제목
st.caption("내가 어떤 상황인지 파악하고 어떻게 해결할지 궁금하다면 LOWLAW와 대화하면서 해결해보세요") #st 캡션text
st.divider() #st구분선

if 'generated' not in st.session_state: # st generated 초기화 설정
    st.session_state['generated'] = []

if 'past' not in st.session_state: # st past 초기화 설정
    st.session_state['past'] = []

with st.form('form', clear_on_submit=True): #st text box
    user_input = st.text_input('당신: ', '') #st 사용자input text
    submitted = st.form_submit_button('전송') #st 전송버튼

# 문장벡터 계산
embeddings = model.encode([user_input]) if user_input is not None else None

# Elasticsearch에서 embedding 필드 값 검색
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["question","answer","law", "prec", "embedding"]
}

response = es.search(index="legal_qa", body=query, size=10)

# 가장 높은 코사인 유사도 값 초기화
max_cosine_similarity = -1
best_answer = ""

if submitted and user_input : # 사용자가 text를 입력하였다면
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
        
        st.session_state.past.append(user_input) # 사용자 text append
        st.session_state.generated.append(best_answer) # 가장 유사한 답변 append


for i in range(len(st.session_state['past'])): #st 메세지 띄우기
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    if len(st.session_state['generated']) > i:
        message(st.session_state['generated'][i], key=str(i) + '_bot')
   
