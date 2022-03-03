import streamlit as st
from streamlit_quill import st_quill

st.set_page_config(layout="wide")
params=st.experimental_get_query_params()
if 'user' in params and 'project' in params and 'assessment' in params:
    user=params['user']
    project=params['project']
    assessment=params['assessment']
    filename=f"{user}_{project}_{assessment}.html"
    try:
        with open(filename, 'r') as f:
            content=f.read()
    except:
        content=""
    with st.form(k="my_form"):
        out = st_quill(value=str(content),html=True)
        if st.form_submit_button("Save"):
            with open(filename, 'w') as f:
                f.write(out)