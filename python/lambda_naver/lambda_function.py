from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
#import boto3

def lambda_handler(event, context):
    #dynamodb = boto3.resource('dynamodb')
    #table_name = 'LOWLAW_naver'  # 테이블 이름
    
    all_url_list = []
    
    title_list =[]  
    question_list = []
    date_list = []
    q_id_list = []
    pageNum = 1
    q_id = 1
    today = datetime.today().strftime("%Y%m%d")
    today = int(today)
    
    while True:
        if pageNum < 5 :
            break
        url_list = []
        url_page="https://kin.naver.com/qna/expertAnswerList.naver?dirId=60202&queryTime=2023-07-22%2018%3A12%3A49&page="+str(pageNum)
        response = urlopen(url_page)
        soup = BeautifulSoup(response,"html.parser")
        
        for href in soup.find("div",class_="board_box").find_all("tr"):
            get_url = href.find("a")["href"]
            get_url = "https://kin.naver.com"+get_url
            url_list.append(get_url)
            
        pageNum+=1
        
        i = 1
        while True:
            if i > 20:
                i = 0
                break
            
            url = url_list[i]
            response = urlopen(url)
            soup = BeautifulSoup(response,"html.parser")
            title = soup.select_one(".title").get_text()
            title = title.lstrip()
            
            if soup.select_one(".c-heading__content") is None :
                question = title
            else:
                question = soup.select_one(".c-heading__content").get_text()
                question = question.lstrip()
            date = soup.select_one(".c-userinfo__info").get_text()
            date = date.replace("작성일","")
            date = date.replace("끌올","")
            date = date.replace(".","")
            date = int(date)
            if '시간' in date:
                date = today
            
            all_url_list.append(url)
            title_list.append(title)
            question_list.append(question)
            date_list.append(date)
            q_id_list.append(today+"."+str(q_id))
            """
            table = dynamodb.Table(table_name)
            table.put_item(
                Item={
                    'date+id': today + "." + str(q_id),
                    'question': question,
                    'title': title,
                    'date' : date,
                    'url': url,
                }
            )
            
             """   
                
            i += 1
            q_id += 1


        



