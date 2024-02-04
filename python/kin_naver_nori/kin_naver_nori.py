from elasticsearch import Elasticsearch

es_cloud_id = ""
es_username = ""
es_pw = ""

es = Elasticsearch(cloud_id=es_cloud_id,basic_auth=(es_username,es_pw))

#kin_naver_nori라는 인덱스가 es에 저장되어있으면 삭제
if es.indices.exists(index="kin_naver_nori"):
    es.indices.delete(index="kin_naver_nori")
    
#노리 분석기 설정
nori_analyzer_settings = {
    "type":"custom",
    "tokenizer" : "nori_tokenizer",
    "filter":["nori_filter"],
}
nori_tokenizer_settings = {
    "type": "nori_tokenizer",
    "decompound_mode": "none"
}
decompound_filter_settings={
    "type" : "nori_part_of_speech",
    "stoptags": ["J","IC","E", "MAG", "MAJ", "MM", "SP", "SSC", "SSO", "SC", "SE","SF","SN","XPN", "XSN", "XSV", "UNA",
                 "NR","VV","VA","SP","XR","NP","NNB","NNBC","MM","MAJ","MAG","VSV","VCP","VX","VSV","XSN","XSV","E","NA","SL","XR","XSA"] 
}

es.indices.create(index="kin_naver_nori",body={
    "settings":{
        "analysis":{
            "analyzer":{
                "nori_analyzer" : nori_analyzer_settings
            },
            "tokenizer" : {
                "nori_tokenizer":nori_tokenizer_settings
            },
            "filter":{
                "nori_filter":decompound_filter_settings
            }
        }
    }    
})

def token_should_exclude(token):
    excluded_words = ["있","없","저희","수","원","안녕","개월","때","후","거","정도","일","월","전","같","답변","말","시"]
    return token["token"] in excluded_words

#kin_naver에서 question만 가져와서 저장
index_name = "kin_naver_nori_db"
query = {
    "_source": "question",
    "query": {
        "match_all": {}
    },
    "size": 10000,  # 한 번에 가져올 문서 수
    "scroll": "1m"  # Scroll 유지 시간
}

# Elasticsearch 쿼리 실행
result = es.search(index=index_name, body=query)
total_hits = result["hits"]["total"]["value"]  # 전체 문서 수
scroll_id = result["_scroll_id"]


# 해당 단어는 keyword에 저장 X

nori_api_url = "http://localhost:9200/_analyze"
new_index_name = "kin_naver_nori"


while True:
    hits = result.get("hits", {}).get("hits", [])
    if not hits:
        break

    for idx, hit in enumerate(hits):
        question_text = hit["_source"].get("question", "")
        payload = {
            "analyzer": "nori_analyzer",
            "text": question_text
        }

        response = es.indices.analyze(index=new_index_name, body=payload)
        tokens = [token["token"] for token in response.get("tokens", []) if not token_should_exclude(token)]
        new_doc = {
            "question_keywords": tokens
        }
        es.index(index=new_index_name, id=idx, body=new_doc)

    # Scroll API로 다음 페이지 가져오기
    result = es.scroll(scroll_id=scroll_id, scroll="1m")

    # 전체 문서 수를 넘어가면 루프 종료
    if idx + 1 >= total_hits:
        break

# Scroll API 사용 후 Scroll ID로 검색 컨텍스트를 닫아줘야 합니다.
es.clear_scroll(scroll_id=scroll_id)





