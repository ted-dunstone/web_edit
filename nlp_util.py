import streamlit as st
from bs4 import BeautifulSoup
from streamlit_quill import st_quill

import requests,json,random
from io import BytesIO
from math import log
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import re

headers = {"Authorization": "Bearer api_inDIvlkNTiAfRrjLpJhMltbSIiMUmTBvab"}

@st.cache(ttl=24*60*60.0)
def fetch(url,params):
    return requests.get(url, params = params)       

def removeSentance(find_str):
    sentances = re.split(r'[.]\s', find_str)
    sentances = [s for s in sentances if len(s)>3 and 
        s!='In the U.S' and 
        s.find('National Suicide Prevention Line')==-1 and 
        s.find("For confidential support call the")==-1 and 
        s.find("suicide")==-1 and 
        s.find('samaritans')==-1 and
        s.find('Article Topics')==-1 and
        s.find('Forbidden for url')==-1 and
        s.find('http')]
    return '. '.join(sentances)

@st.cache(persist=True,max_entries=200)
def summarize(input: str,min_length=200,max_length=1000,temperature=0.7,use_gpu=False):
    payload = {
		"inputs":input,
		"parameters":{"min_length":min_length,"max_length":max_length,"temperature":temperature}
	}
    response = requests.post("https://api-inference.huggingface.co/models/facebook/bart-large-cnn", headers=headers, data=json.dumps(payload))
    response = response.json()
    if len(response)>0:
        try:
            response = removeSentance(response[0]['summary_text'])
        except:
            pass
    else:
        st.exception(response)
    return response 

def get_histogram_dispersion(im):
    histogram=im.histogram()
    log2 = lambda x:log(x)/log(2)

    total = len(histogram)
    counts = {}
    for item in histogram:
        counts.setdefault(item,0)
        counts[item]+=1

    ent = 0
    for i in counts:
        p = float(counts[i])/total
        ent-=p*log2(p)
    return -ent*log2(1/ent)

@st.cache(persist=True,max_entries=200)
def gptj(input: str, max_len=200,temperature= 0.8,num_return_sequences= 1,use_gpu=False,return_full_text=False):
	""" Some docs """
	payload = {
		"inputs":input,
		"parameters":{"max_new_tokens":max_len,"temperature":temperature,"top_p":None,"num_return_sequences":num_return_sequences,"return_full_text":return_full_text},
		"options":{"use_gpu":use_gpu}
	}
	response = requests.post("https://api-inference.huggingface.co/models/EleutherAI/gpt-j-6B", headers=headers, data=json.dumps(payload))
        
	return response.json()

def removeSentance(find_str):
    sentances = re.split(r'[.]\s', find_str)
    sentances = [s for s in sentances if len(s)>3 and s!='In the U.S' and s.find('National Suicide Prevention Line')==-1 and s.find("For confidential support call the")==-1 and s.find("suicide")==-1 and s.find('samaritans')==-1]
    return '. '.join(sentances)


def gpt_proc(input: str, max_len=200,temperature= 0.7,num_return_sequences= 1,use_gpu=False,return_full_text=False):
    out=gptj(input, max_len,temperature,num_return_sequences,use_gpu,return_full_text)
    responses = [r['generated_text'] for r in out]
    return [removeSentance(r) for r in responses]

@st.cache(ttl=24*60*60.0)
def select_best_image(top_list):
    tl=top_list.copy()   
    random.shuffle(tl)
    ## choose a good image for the intro
    top_idx = 0
    for idx,articles in enumerate(tl):
        try:
            response = requests.get(replacments[articles]['top_image'])
            img = Image.open(BytesIO(response.content))
            if get_histogram_dispersion(img)>30:
                top_idx=idx
                break
        except:
            pass
    return tl[top_idx]

