import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DBMS Project: Chess Tournament Management System"   ,
    page_icon="♟️"
)

st.title("Chess Tournament Management System")
st.text("Aadrito Datta & Souradeep Dutta")
col1,col2= st.columns(2)
col1.link_button("Github","https://github.com/souradeepdutta/Tournament-Management-System",use_container_width=True)
st.markdown("""## Problem Statement""")
st.markdown(""" ***A new chess tournament management system that is designed to
address these challenges*** """)
st.markdown(""" Current chess tournament systems stifle growth with:
- Limited data analysis hindering informed decision-making
- Lack of accessibility and scalability for large-scale events
- Hard for competitors to query large amounts of data
- Hard to maintain up-to-date information about player eligibility
- Chess software is out-of-date
- Lack of a centralized system to handle ELO updates making the system more error-prone
""")
st.markdown("""### Features""")
st.markdown("""- feature""")
st.markdown("### ER Model")
st.image("Picture.png")





