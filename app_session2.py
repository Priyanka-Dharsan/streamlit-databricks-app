import streamlit as st

st.title("My first Streamlit app on Databricks")
name = st.text_input("Your name")
if name:
    st.write(f"Hello, {name}!")
