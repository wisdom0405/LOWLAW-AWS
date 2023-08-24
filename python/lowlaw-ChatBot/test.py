# 그냥 test
import streamlit as st
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
st.title("LOWLAW")

if 'generated' not in st.session_state: # st generated 초기화 설정
    st.session_state['generated'] = []

if 'past' not in st.session_state: # st past 초기화 설정
    st.session_state['past'] = []

# ChatBot의 환영인사
with st.chat_message("assistant"):
    st.write("안녕하세요! LOWLAW에 오신 것을 환영합니다👋")
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

response = es.search(index="legal_qa", body=query, size=100)

# 가장 높은 코사인 유사도 값 초기화
max_cosine_similarity = -1
best_answer = ""

if user_input : # 사용자가 user_input를 입력하였다면
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
        
    st.session_state.past.append(user_input) # 사용자 user_input append
    st.session_state.generated.append(best_answer) # 가장 유사한 답변 append


for i in range(len(st.session_state['past'])): # 메세지 띄우기
    with st.chat_message("user"):
        st.write(st.session_state['past'][i])
    if len(st.session_state['generated']) > i:
        with st.chat_message("assistant"):
            st.write(st.session_state['generated'][i])
