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
    with st.form(key="my_form"):
        #out = st_quill(value=content,html=True)
        out=st.text_area(content,key="my_textarea")
        if st.form_submit_button("Save"):
            with open(filename, 'w') as f:
                f.write(out)
                st.info("written")