import stripe
import urllib.parse
import streamlit as st
from datetime import datetime
import dynamodb as db
import os
from dotenv import load_dotenv

load_dotenv(".env")

try:
    stripe_link_test = st.secrets.get("stripe_link_test")
except FileNotFoundError:
    stripe_link_test = os.getenv("stripe_link_test")
try:
    stripe_api_key_test = st.secrets.get("stripe_api_key_test")
except FileNotFoundError:
    stripe_api_key_test = os.getenv("stripe_api_key_test")
try:
    stripe_link = st.secrets.get("stripe_link")
except FileNotFoundError:
    stripe_link = os.getenv("stripe_link")
try:
    stripe_api_key = st.secrets.get("stripe_api_key")
except FileNotFoundError:
    stripe_api_key = os.getenv("stripe_api_key")


def get_api_key() -> str:
    testing_mode = st.secrets.get("testing_mode")#st.secrets.get("testing_mode", False)
    return (
        stripe_api_key_test #st.secrets["stripe_api_key_test"]
        if testing_mode
        else stripe_api_key
    )


def is_active_subscriber(email: str) -> bool:
    stripe.api_key = get_api_key()
    customers = stripe.Customer.list(email=email)
    try:
        customer = customers.data[0]
    except IndexError:
        return False

    subscriptions = stripe.Subscription.list(customer=customer["id"])

    return len(subscriptions) > 0

def get_customer_id(email):
    """returns the Stripe user id by providing the user e-mail"""
    stripe.api_key = get_api_key()
    customers = stripe.Customer.list(email=email)
    try:
        customer = customers.data[0]
    except IndexError:
        return False
    return customer.id

def redirect_button(
    text: str,
    customer_email: str,
    color="#FD504D",
):
    testing_mode = os.getenv("testing_mode")#st.secrets.get("testing_mode", False)
    encoded_email = urllib.parse.quote(customer_email)
    stripe.api_key = get_api_key()
    stripe_link = (
        st.secrets["stripe_link_test"]
        if testing_mode
        else st.secrets["stripe_link"]
    )
    button_url = f"{stripe_link_test if testing_mode else stripe_link}?prefilled_email={encoded_email}"

    st.markdown(
        f"""
    <a href="{button_url}" target="_blank">
        <div style="
            display: inline-block;
            padding: 0.5em 1em;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 3px;
            text-decoration: none;">
            {text}
        </div>
    </a>
    """,
        unsafe_allow_html=True,
    )



def display_user_info(email):
    #User information
    st.sidebar.markdown(f"### Seja bem vindo, {db.get_user(email)['username']['S']}")
    email_html = """ <p> E-mail: %s </p>""" % email
    st.sidebar.markdown(email_html, unsafe_allow_html=True)
    st.sidebar(redirect_button)
    if not is_active_subscriber(email):
        st.sidebar.subheader(f'Assinatura: Inativa')
    else:
        customers = stripe.Customer.list(email=email, limit=1)
        customer_id = customers.data[0].id
        subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
        if subscriptions.data:
            subscription = subscriptions.data[0]

            current_period_start_timestamp = subscription.current_period_start
            current_period_end_timestamp = subscription.current_period_end

            current_period_start = datetime.utcfromtimestamp(current_period_start_timestamp)
            current_period_end = datetime.utcfromtimestamp(current_period_end_timestamp)
        st.sidebar.markdown(f'Subscription date: {current_period_start.strftime("%d/%m/%Y")}')
        st.sidebar.markdown(f'Subscription ends: {current_period_end.strftime("%d/%m/%Y")}')

