import requests

# 엘라스틱 앱서치 엔진 정보
engine_name = "prec-content"
base_url = base_url = "http://lowlaw.ent.ap-northeast-2.aws.elastic-cloud.com/api/as/v1/engines/{engine_name}/top_queries"

# API 키 설정
api_key = "private-egnzqo7tt7fd6fngz13mmox9"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
#url 생성
url = base_url.format(engine_name=engine_name)

#매개변수 추가
params = {
    "size" : 5
}

response = requests.get(url, headers=headers,params=params)

print("여기까지 완")
if response.status_code == 200:
    top_queries = response.json()
    print(top_queries)
else:
    print("Error:", response.status_code)