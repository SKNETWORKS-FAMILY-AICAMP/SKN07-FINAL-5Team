import streamlit as st

def show_sidebar():
    st.sidebar.title("메뉴")

    if st.sidebar.button("메인페이지", key="main_page_button"):
        st.switch_page("pages/main_page.py")

    if st.sidebar.button("면접관리", key="mng_1_button"):
        st.switch_page("pages/mng_1.py")

    if st.sidebar.button("서류 제출", key="upload_history_button"):
        st.switch_page("pages/user_pdf_upload.py")

    if st.sidebar.button("채용공고", key="recruit_button"):
        st.switch_page("pages/recruit.py") 

    if st.sidebar.button("모의면접", key="mock_interview_button"):
        st.switch_page("pages/mng_1.py")

    if st.sidebar.button("면접 히스토리", key="history_button"):
        st.switch_page("pages/his1.py")