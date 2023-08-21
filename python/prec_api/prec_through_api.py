import requests
from bs4 import BeautifulSoup
import xmltodict
import json

def get_case_info(case_number):
    base_url = "https://www.law.go.kr/DRF/lawService.do"
    params = {
        "OC": "2yj_1006",
        "target": "prec",
        "ID": case_number,
        "type": "XML"
    }

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, features="xml")

    return soup

if __name__ == "__main__":
    case_number = input("판례의 번호를 입력하세요: ")
    case_info = get_case_info(case_number)

    data = {}
    for item in case_info.find_all():
        if item.name and item.string:
            data[item.name] = item.string

    print(json.dumps(data, indent=4, ensure_ascii=False))
