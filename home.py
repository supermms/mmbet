import streamlit as st
import numpy as np
import pandas as pd
#import csv
#import re
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.stats import binom
#import s3_management
from io import StringIO
import dynamodb as db
import streamlit_authenticator as stauth
#import stripe
import app
#from navigation import make_sidebar

st.set_page_config(page_title="MMBet", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

## Fetch all users into authenticator
users = db.fetch_all_users()
usernames = []
usern = []
names = []
passwords = []

for user in users:
    usernames.append(user['email']['S'])
    usern.append(user['username']['S'])
    names.append(user['name']['S'])
    passwords.append(user['password']['S'])

credentials = {'usernames': {}}
for index in range(len(usernames)):
    credentials['usernames'][usernames[index]] = {'username': usern[index], 'name':names[index], 'password': passwords[index]}


print(credentials)

Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=0)

#Estilos

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.markdown("<h1 style='text-align: center;'>MMBet</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Apostas esportivas baseadas em IA</p>", unsafe_allow_html=True)
st.markdown("""<p class="show-on-cel" style='text-align: center; display:none; color:#FC8181;"'>Esta aplicação não é responsiva para celulares. Selecione a versão para computador para ter uma melhor experiência.</p>""", unsafe_allow_html=True)

st.write("")
    
name, authentication_status, username = Authenticator.login(fields={'Form name':'Login', 'Username':'E-mail', 'Password': 'Password', 'Login':'Login'}, location='main')

info, info1 = st.columns(2)

if authentication_status == False:
    db.sign_up()

if username:
    print(username)
    if username in usernames:
        if authentication_status:
            st.markdown(f"""<p style='text-align: center;'> {username} </p>""", unsafe_allow_html=True)
            st.session_state.logged_in = True
            app.main(username)
        elif not authentication_status:
            with info:
                st.error('Incorrect Password or username')
        else:
            with info:
                st.warning('Please feed in your credentials')
    else:
        with info:
            st.warning('Username does not exist, Please Sign up')

st.markdown("""<p style='text-align: center;'>Desenvolvido por <a href='https://linkedin.com/in/matheusmsa'>Matheus Moreno Sá</a></p>""", unsafe_allow_html=True)
st.markdown("""<p style='text-align: center;'>Está gostando da ferramenta? Ela é 100% gratuita. Considere apoiar o desenvolvimento me pagando um cafézinho <a href='https://nubank.com.br/pagar/30c23/Xvbp895w2O'>via pix</a></p>""", unsafe_allow_html=True)



