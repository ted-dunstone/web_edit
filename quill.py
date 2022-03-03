import streamlit as st
from streamlit_quill import st_quill

st.set_page_config(layout="wide")
params=st.experimental_get_query_params()
if 'user' in params and 'project' in params and 'assessment' in params:
    user=params['user']
    project=params['project']
    assessment=params['assessment']
    filename=f"{user}_{project}_{assessment}.html"
    content=""
    with open(filename, 'r') as f:
        content=f.read()
    out = st_quill(value=str(content),html=True)
    if out != content:
        with open(filename, 'w') as f:
            f.write(out)