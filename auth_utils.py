from mmap import PAGESIZE
import streamlit as st
import extra_streamlit_components as stx
import streamlit_authenticator as stauth
import os.path
import os,json
import psycopg2
from streamlit_ace import st_ace
from streamlit_option_menu import option_menu

conn = None
user_name = None

# DB Setup

#@st.experimental_singleton
def get_db_conn():
    DATABASE_URL = os.environ['DATABASE_URL'] if 'DATABASE_URL' in os.environ else None
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        return conn
    return None

cookie_manager = None

@st.cache(allow_output_mutation=True)
def get_manager(key):
    return stx.CookieManager(key=key)

def set_manager(key):
    global cookie_manager
    cookie_manager = get_manager(key)


def load_config(user_name):
    if conn:
        cur=conn.cursor()
        cur.execute(f"SELECT config from config WHERE username='{user_name}'")
        if cur.rowcount>0:
            res=cur.fetchone()
            return json.loads(res[0])
        else:
            return {}
    else:    
        if os.path.exists(user_name+".json"):
            with open(user_name+".json") as f:
                return json.load(f)
        else:
            return {}

def init_config(config_list,config_params, user_name):
    
    #st.write(st.session_state.config)    
    st.session_state.config=cookie_manager.get(cookie="config")
    
    if st.session_state.config is None or st.session_state.config == 'None' or st.session_state.config == {}:
        st.session_state.config=load_config(user_name)
    
    namelook_up={}
    for n in config_list:
        if n not in st.session_state.config:
            st.session_state.config[n]= {}
        if "name" in st.session_state.config[n]:
            namelook_up[n] = st.session_state.config[n]["name"]
            if namelook_up[n]=="":
                namelook_up[n] = n
        else:
            namelook_up[n] = n
        for k,v in config_params.items():
            if k not in st.session_state.config[n]:
                st.session_state.config[n][k]=v
    return namelook_up

def get_config(name):
    return st.session_state.config[name]

def set_config(name,config):
    cookie_manager.set("config",st.session_state.config) 
    st.session_state.config[name]=config
    with open(user_name+".json","w") as f:
        json.dump(st.session_state.config,f)

def save_config(name,config):
    if conn:
        cur=conn.cursor()
        config_json = json.dumps(st.session_state.config)
        cur.execute(f""" INSERT INTO config(username,config) VALUES(%s,%s) ON CONFLICT (username) DO
        UPDATE SET config=%s """,(user_name,config_json,config_json))
        conn.commit()

names = ['Ted Dunstone','Test Test','System Admin']
usernames = ['ted','test','Admin']
passwords = ['123','456','123']
hashed_passwords = stauth.hasher(passwords).generate()

def login_component():
    global conn
    global user_name
    conn=get_db_conn()
    if conn:
        cur=conn.cursor()
        cur.execute("SELECT username,hashed_passwords from user_tables")
        rows = cur.fetchall()
        if cur.rowcount>0:
            names.extend([row[0] for row in rows])
            usernames.extend([row[0] for row in rows])
            hashed_passwords.extend([row[1] for row in rows])
            
    authenticator = stauth.authenticate(names,usernames,hashed_passwords,
        'some_cookie_name','some_signature_key',cookie_expiry_days=30)
    user_name, authentication_status = authenticator.login('Login','sidebar')
    if not authentication_status or st.session_state['authentication_status'] == False:
        if authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')
            if conn and st.checkbox('Create Account'):
                with st.expander("Create Account",True):
                    user_name = st.text_input("Enter an email")
                    if user_name:
                            st.info('Creating account for '+user_name)
                            password = st.text_input("Enter a password", type="password")
                            if st.button('Done') and password:
                                hashed_password = str(stauth.hasher([password]).generate()[0])
                                cur.execute(f""" INSERT INTO user_tables(username,hashed_passwords) VALUES(%s,%s) """,(user_name,hashed_password))
                                conn.commit()
                                st.success('Account created')
                                st.info('You may now login')
                    
                
                    #cur.execute("INSERT username,hashed_passwords from config WHERE username='%s'")
        
        st.session_state.config = {}
        cookie_manager.set("config",st.session_state.config) 
        st.stop()
    return user_name
