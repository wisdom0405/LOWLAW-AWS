#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

input_value = input("입력값을 입력하세요: ")  # 입력값 받기
keywords = input_value.split(',')  # 입력값을 쉼표 기준으로 분리하여 리스트로 저장

data = []
for keyword in keywords:
    keyword_list = keyword.strip().split()  # 단어를 띄어쓰기로 구분하여 리스트로 저장
    
    # '후단'과 '단서' 단어 제거
    for word in keyword_list:
        if word.endswith('후단') or word.endswith('단서'):
            keyword_list.remove(word)
    
    law = ''
    jo, hang, ho, mok = '', '', '', ''
    
    # 단어 리스트를 역순으로 순회하며 목호항조 순서로 찾음
    for word in keyword_list[::-1]:
        if '목' in word:
            mok = word
        elif '호' in word:
            ho = word
        elif '항' in word:
            hang = word
        elif '조' in word:
            jo = word
            break
    
    # 남은 단어를 법령명_한글 열에 저장
    remaining_words = ' '.join(keyword_list[:keyword_list.index(jo)])
    law = law + ' ' + remaining_words
    
    data.append({
        '법령명_한글': law.strip(), 
        '조문번호': jo,
        '항번호': hang,
        '호번호': ho,
        '목번호': mok
    })

df = pd.DataFrame(data)
print(df)

