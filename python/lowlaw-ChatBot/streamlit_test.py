import streamlit as st
from sentence_transformers import SentenceTransformer, util
from elasticsearch import Elasticsearch
from PIL import Image
import re

es_cloud_id = ""
es_username = ""
es_pw = ""

es = Elasticsearch(cloud_id=es_cloud_id, basic_auth=(es_username, es_pw))

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


@st.cache_data() # st 캐싱 (로컬캐시에 저장)

def cached_model():
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    return model

def load_image(img_file): # st 이미지 불러오기 함수
    img = Image.open(img_file)
    return img
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
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["question","answer","law", "prec", "embedding"]
}

response = es.search(index="legal_qa", body=query, size=100)


# 문장벡터 계산


# Elasticsearch에서 embedding 필드 값 검색

#질문에 대한 답변 저장
sources = {}


# 가장 높은 코사인 유사도 값 초기화
max_cosine_similarity = -1
best_answer = ""



def button_law() :
    st.session_state.messages.append({"role" : "assistant", "content" : "뀨"})
def button_prec() :
    st.session_state.messages.append({"role" : "assistant", "content" : "퓨"})  

def addChatBot():
    source = sources["source"]
    best_answer = source["answer"]
    related_law = source.get("law", None) # 필드에 데이터가 존재하면 law 값을 가져오고 존재하지 않으면 None 반환
    related_prec = source.get("prec", None)

    best_answer = re.sub(r'\((.*?)\)', lambda x: x.group(0).replace('.', ' '), best_answer)
    st.session_state.messages.append({"role" : "assistant", "content" : best_answer})

    if related_law:
        related_law_list = related_law.split(",")
        st.markdown(f"**:red[참조법령]** :scales:")
        for law in related_law_list: # 참조판례 리스트 안에 있는 내용 각각 버튼으로 출력  
            st.session_state.messages.append({"role": "📖", "content": f"**:red[참조법령] {st.button(law.strip(),on_click=lambda:button_law())}**"})
            # st.session_state.messages.append({"role": "📖", "content": f"**:red[참조법령] {law.strip()}**"})

    if related_prec: # 만약 참조판례가 있다면
        related_prec_list = related_prec.split(",")  # ','로 구분하여 리스트로 변환
        st.markdown(f"**:red[참조판례]** :scales:")
        for prec in related_prec_list: # 참조판례 리스트 안에 있는 내용 각각 버튼으로 출력  
            st.session_state.messages.append({"role": "⚖️", "content": f"**:red[참조판례] {st.button(prec.strip(),on_click=lambda:button_prec())}**"})
            # st.session_state.messages.append({"role": "⚖️", "content": f"**:red[참조판례] {prec.strip()}**"})

def user_submit():
    
    # st.chat_message("user").markdown(user_input)

    # 사용자의 user_input을 chat history에 append

    for hit in response["hits"]["hits"]:
        doc_embedding = hit["_source"]["embedding"]
    
        # Elasticsearch에서 가져온 'embedding' 값을 문자열에서 리스트로 변환
        doc_embedding = [float(value) for value in doc_embedding.strip("[]").split(", ")]
    
        cosine_similarity = util.pytorch_cos_sim(embeddings, [doc_embedding]).item()
    
        if cosine_similarity > max_cosine_similarity:
            max_cosine_similarity = cosine_similarity
            source = hit["_source"]
            # best_answer = source["answer"]
            # related_law = hit["_source"].get("law", None) # 필드에 데이터가 존재하면 law 값을 가져오고 존재하지 않으면 None 반환
            # related_prec = hit["_source"].get("prec", None)
        
        if max_cosine_similarity>0.7:
            sources["source"] = source
            addChatBot()
    else:
        # assistant의 답변 chat message에 띄워주기 (0.7 이하일 때)
        with st.chat_message("assistant"):
            st.markdown("질문에 대한 답변을 찾을 수 없어요:cry: 상황에 대해서 정확히 입력해주세요!")
        st.session_state.messages.append({"role" : "assistant", "content" : "질문에 대한 답변을 찾을 수 없어요:cry: 상황에 대해서 정확히 입력해주세요!" }) # 가장 유사한 답변 append

# 사용자에게 문장 입력 받기
user_input = st.chat_input(placeholder = "어떤 상황인지 설명해주세요!",on_submit=user_submit())
embeddings = model.encode([user_input])[0] if user_input is not None else None
