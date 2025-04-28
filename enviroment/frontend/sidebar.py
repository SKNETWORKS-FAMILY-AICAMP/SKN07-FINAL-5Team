import streamlit as st
from streamlit_option_menu import option_menu

# 사이드바 메뉴를 보여주는 함수 정의
def show_sidebar():
    # 세션 상태에 'selected_menu' 키가 없다면 기본값을 '메인페이지'로 설정
    if "selected_menu" not in st.session_state:
        st.session_state["selected_menu"] = "메인페이지"

    with st.sidebar:
        st.markdown("""
            <div style='
                text-align: center;
                padding: 20px 0 12px 0;
                font-size: 36px;
                font-weight: bold;
                color: #4b8def;
                border-bottom: 2px solid #ddd;
                margin-bottom: 16px;
            '>
                Menu
            </div>
        """, unsafe_allow_html=True)

        선택된_메뉴 = option_menu(
            menu_title="",  # 메뉴 제목 생략
            options=[  # 메뉴 항목들
                "메인페이지", 
                "서류제출", 
                "채용공고", 
                "모의면접", 
                "면접 히스토리"
            ],
            icons=[  # 각 메뉴에 대한 아이콘
                "house", 
                "kanban", 
                "briefcase", 
                "mic", 
                "clock-history"
            ],
            # 기본 선택 항목 설정 (세션 상태값 기준)
            default_index=[
                "메인페이지", 
                "서류제출", 
                "채용공고", 
                "모의면접", 
                "면접 히스토리"
            ].index(st.session_state["selected_menu"]),
            styles={
                "container": {
                    "background-color": "#fff",  # 배경색: 밝은 회색
                    "padding": "8px 4px",  # 여백 설정
                    "border-radius": "8px",  # 모서리 둥글게
                },
                "icon": {
                    "font-size": "18px",  # 아이콘 크기
                    "color": "#555"  # 아이콘 색상
                },
                "nav-link": {  # 기본 메뉴 항목 스타일
                    "font-size": "15px",
                    "padding": "10px 18px",
                    "margin": "6px 0",
                    "border-radius": "6px",
                    "color": "#333",  # 글자색
                    "background-color": "#dfedfe",  # 배경색: 흰색
                    "text-align": "left",
                    "transition": "0.3s ease"  # 전환 효과
                },
                "nav-link-selected": {  # 선택된 메뉴 스타일
                    "background-color": "rgb(115 175 252)",  # 선택 시 배경색
                    "color": "#ffffff",  # 선택 시 글자색
                    "font-weight": "bold",  # 굵은 글씨
                    "box-shadow": "inset 4px 0 0 rgb(82 137 211)"  # 선택 표시
                }
            }
        )

    # 메뉴가 바뀌었을 경우 페이지 전환 처리
    if 선택된_메뉴 != st.session_state["selected_menu"]:
        # 세션 상태에 현재 선택된 메뉴 저장
        st.session_state["selected_menu"] = 선택된_메뉴

        # 로딩 스피너 출력
        with st.spinner("⏳ 페이지 이동 중입니다..."):
            # 선택한 메뉴에 따라 해당 페이지로 전환
            if 선택된_메뉴 == "메인페이지":
                st.switch_page("pages/main_page.py")
            elif 선택된_메뉴 == "서류제출":
                st.switch_page("pages/user_pdf_upload.py")
            elif 선택된_메뉴 == "채용공고":
                st.switch_page("pages/recruit.py")
            elif 선택된_메뉴 == "모의면접":
                st.switch_page("pages/mng_2.py")
            elif 선택된_메뉴 == "면접 히스토리":
                st.switch_page("pages/his1.py")

        # 페이지 전환 이후 더 이상의 코드 실행을 막음
        st.stop()
