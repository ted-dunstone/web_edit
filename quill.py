import streamlit as st
from streamlit_quill import st_quill

st.set_page_config(layout="wide")
params=st.experimental_get_query_params()
out = st_quill(value=str(params),html=True)
