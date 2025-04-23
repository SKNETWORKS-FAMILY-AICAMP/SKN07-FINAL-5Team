import os
import openai
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as st
 
def app():
    # API 키 설정
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    url  = st.text_input("이미지 URL을 입력하세요.")
    def get_recruit_img_to_text(image_url):

        # llm
        model = "gpt-4o-2024-08-06"

        # 프롬프트
        messages = [
            { "role": "system", "content": "너는 채용공고 이미지를 분석해 텍스트를 추출한 뒤 다음 항목으로 요약하는 AI야:\
                                        \n1. 기업명: \
                                        \n2. 모집 분야: \
                                        \n3. 모집 직군: \
                                        \n4. 신입/경력 여부:\
                                        \n항목에 맞춰 정확히 정리해서 응답해줘. \
                                        모집 직군이 명확하지 않은 경우, 모집 분야를 기반으로 유추해줘." },
            { "role": "user", "content": [  
                { 
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]} 
            ]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500 
            )
            summary = response.choices[0].message.content
            return summary
        
        except Exception as e:
            return f"에러 발생 : {e}"



    # URL 예시
    #image_url = "https://marketplace.canva.com/EAGbwmG_4QA/1/0/1131w/canva-%ED%9D%B0%EC%83%89%EA%B3%BC-%ED%8C%8C%EB%9E%80%EC%83%89-%EA%B9%94%EB%81%94%ED%95%9C-%EC%8B%A0%EC%9E%85%EC%82%AC%EC%9B%90-%EC%B1%84%EC%9A%A9%EA%B3%B5%EA%B3%A0-%ED%8F%AC%EC%8A%A4%ED%84%B0-CggotBLyXOw.jpg"

    result = get_recruit_img_to_text(url)
    #print(result)



    st.button("Reset", type="primary")
    if st.button("이미지 생성"):
        st.write(result)
    else:
        st.write("Goodbye")
    