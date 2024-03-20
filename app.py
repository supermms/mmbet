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
    st.write(stripe.Customer.list(email=email))
    stripe_auth.redirect_button(text="Inscreva-se agora!", customer_email=email)
    st.write(stripe_auth.stripe_link_test)