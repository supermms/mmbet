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

def main():
    st.title("OI")