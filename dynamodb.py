import boto3
import datetime
import os
import re
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth

# Initialize AWS credentials
load_dotenv(".env")

try:
    aws_access_key_id = st.secrets.get("aws_access_key_id")
except FileNotFoundError:
    aws_access_key_id = os.getenv("aws_access_key_id")
try:
    aws_secret_access_key = st.secrets.get("aws_secret_access_key")
except FileNotFoundError:
    aws_secret_access_key = os.getenv("aws_secret_access_key")


region_name = 'sa-east-1'  # Replace with your desired region

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

def insert_user(email, username, name, password):
    """Returns the user a succesful creation, otherwise raises an error"""
    date_joined = str(datetime.datetime.now())
    return dynamodb.put_item(
        TableName='lbb-report-manager-users',
        Item={
            'email': {'S': email},
            'username': {'S': username},
            'name': {'S': name},
            'date_joined': {'S': date_joined},
            'password': {'S': password},
            'free_tier': {'BOOL':True},
            'free_usos_restantes': {'N': '10'},
            'free_ultimo_uso': {'S': date_joined}
        }
)

def get_user(email):
    """If not found, the function will return None"""
    return dynamodb.get_item(
    TableName='lbb-report-manager-users',
    Key={
        'email': {'S': email}
    }
    )['Item']

def get_free_uses(email):
    return dynamodb.get_item(
    TableName='lbb-report-manager-users',
    Key={
        'email': {'S': email}
    }
    )['Item']['free_usos_restantes']['N']


def get_email(username):
    return dynamodb.get_item(
    TableName='lbb-report-manager-users',
    Key={
        'username': {'S': username}
    }
    )['Item']['email']['S']

def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return dynamodb.delete_item(
    TableName='lbb-report-manager-users',
    Key={
        'username': {'S': username}
    }
    )

def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False

def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False

def fetch_all_users():
    response = dynamodb.scan(
        TableName='lbb-report-manager-users'
    )
    users = response['Items']
    # while 'LastEvaluatedKey' in response:
    #     response = dynamodb.scan(
    #         TableName='mmb-users',
    #         ExclusiveStartKey=response['LastEvaluatedKey']
    #     )
    # users.extend(response['Items'])
    return users

def get_all_emails():
    response = dynamodb.scan(
        TableName='lbb-report-manager-users'
    )
    users = response['Items']
    # while 'LastEvaluatedKey' in response:
    #     response = dynamodb.scan(
    #         TableName='mmb-users',
    #         ExclusiveStartKey=response['LastEvaluatedKey']
    #     )
    # users.extend(response['Items'])

    items = [user['email'] for user in users]
    emails = [e['S'] for e in items]
    return emails

def handle_last_free_use_date(email):
    format_string = "%Y-%m-%d %H:%M:%S.%f"
    last_use_date_string = get_user(email)['free_ultimo_uso']['S']
    last_use_date = datetime.datetime.strptime(last_use_date_string, format_string)
    if last_use_date.date() < datetime.datetime.now().date():
        return True
    else:
        return False


def update_free_uses(email):
    """ Remove um uso restante do usuário e altera a data do ultimo uso, caso o ultimo uso tenha sido ontem, reseta e remove um. Esta funçãoa assume que o numero de usos restantes é maior que zero"""
    if handle_last_free_use_date(email):
        dynamodb.update_item(TableName='lbb-report-manager-users',
        Key={
            'email': {'S': email},
        },
        UpdateExpression='SET free_usos_restantes = 10 - :val, free_ultimo_uso = :dat',
        ExpressionAttributeValues={
            ':val': {'N': '1'},
            ':dat': {'S': str(datetime.datetime.now())}
        }
        )

    else:
        dynamodb.update_item(TableName='lbb-report-manager-users',
        Key={
            'email': {'S': email},
        },
        UpdateExpression='SET free_usos_restantes = free_usos_restantes - :val, free_ultimo_uso = :dat',
        ExpressionAttributeValues={
            ':val': {'N': '1'},
            ':dat': {'S': str(datetime.datetime.now())}
        }
        )




def get_all_usernames():
    response = dynamodb.scan(
        TableName='lbb-report-manager-users'
    )
    users = response['Items']
    # while 'LastEvaluatedKey' in response:
    #     response = dynamodb.scan(
    #         TableName='mmb-users',
    #         ExclusiveStartKey=response['LastEvaluatedKey']
    #     )
    # users.extend(response['Items'])

    items = [user['username'] for user in users]
    usernames = [u['S'] for u in items]
    return usernames



def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        name = st.text_input(':blue[Name]', placeholder='Enter Your Name')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        if email:
            if validate_email(email):
                if email not in get_all_emails():
                    if validate_username(username):
                        if username not in get_all_usernames():
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        # Add User to DB
                                        hashed_password = stauth.Hasher([password2]).generate()
                                        insert_user(username, name, email, hashed_password[0])
                                        st.success('Account created successfully!!')
                                        st.balloons()
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is too Short')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Username Already Exists')

                    else:
                        st.warning('Invalid Username')
                else:
                    st.warning('Email Already exists!!')
            else:
                st.warning('Invalid Email')

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)

        with btn3:
            st.form_submit_button('Sign Up')
        return True
