import streamlit as st
import numpy as np
import pandas as pd
import csv
import re
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.stats import binom
#import s3_management
from io import StringIO
import dynamodb as db
import streamlit_authenticator as stauth
import stripe
import stripe_auth

def main(email):
    ##Check 
    stripe_auth.display_user_info(email)
    if stripe_auth.is_active_subscriber(email):
        st.write(stripe.Customer.list(email=email))
    else:
        button_url = f"{stripe_auth.stripe_link_test}?prefilled_email={email}"
        st.sidebar.link_button("Inscreva-se agora!", button_url)
        st.alert("Inscra-se utilzando o mesmo e-mail de cadastro no MMbet. Inscrições com e-mails diferentes não serão reconehcidas.")