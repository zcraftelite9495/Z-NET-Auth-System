#!/bin/python3
import sys
import base64
import os.path

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]

TYPE = sys.argv[1]
if TYPE == "verify":
  twofa_code = sys.argv[2]
  ApplicationName = sys.argv[3]
  reciever = sys.argv[4]
elif TYPE == "app":
  USER = sys.argv[2]
  twofa_entry_name = sys.argv[3]
  twofa_answer = sys.argv[4]
  ApplicationName = sys.argv[5]
elif TYPE == "failure":
  USER = sys.argv[2]
  twofa_entry_name = sys.argv[3]
  twofa_answer = sys.argv[4]
  ApplicationName = sys.argv[5]

if TYPE != "verify":
  twofa_auth_type = twofa_entry_name + ": " + twofa_answer

if TYPE != "verify":
  if twofa_entry_name == "":
    twofa_auth_type = "no selected method"
  elif twofa_answer == "":
    twofa_answer = "blank"

if TYPE == "app":
  msg_prefix = " authenticated "
elif TYPE == "failure":
  msg_prefix = " failed to authenticate "
elif TYPE == "cancelation":
  msg_prefix = " canceled authentication for "

def twofa_warning():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("/home/[profile]/.config/Z-NET/MailClientService/token.json"):
    creds = Credentials.from_authorized_user_file("/home/[profile]/.config/Z-NET/MailClientService/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "/home/[profile]/.config/Z-NET/MailClientService/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("/home/[profile]/.config/Z-NET/MailClientService/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content("Z-NET Authentication System Warning: " + USER + msg_prefix + ApplicationName + " using " + twofa_auth_type + ".") 

    message["To"] = alertmail
    message["From"] = "outgoing-email@example.com"
    message["Subject"] = "Z-NET"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message

def verification_code_twofa():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("/home/[profile]/.config/Z-NET/MailClientService/token.json"):
    creds = Credentials.from_authorized_user_file("/home/[profile]/.config/Z-NET/MailClientService/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "/home/[profile]/.config/Z-NET/MailClientService/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("/home/[profile]/.config/Z-NET/MailClientService/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content("Z-NET Verification Code: " + "Your verification code for " + ApplicationName + " is " + twofa_code + ", do not share this code with anyone else.") 

    message["To"] = reciever
    message["From"] = "outgoing-email@example.com"
    message["Subject"] = "Z-NET Verification"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message

if TYPE == "app":
  alertmail = "phone-mms-email@example.com"
  twofa_warning()
  alertmail = "first-email@example.com"
  twofa_warning()
elif TYPE == "failure":
  alertmail = "phone-mms-email@example.com"
  twofa_warning()
  alertmail = "first-email@example.com"
  twofa_warning()
elif TYPE == "cancelation":
  alertmail = "phone-mms-email@example.com"
  twofa_warning()
  alertmail = "first-email@example.com"
  twofa_warning()
elif TYPE == "verify":
  verification_code_twofa()