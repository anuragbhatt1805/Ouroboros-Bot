import os
from twilio.rest import Client
from dotenv import load_dotenv
import random


load_dotenv("./connection/credentials.env")
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
message_sid = os.environ['TWILIO_MESSAGE_SID']

client = Client(account_sid, auth_token)

async def send_otp(mobile, code):
    try:
        if len(mobile) == 10:
            mobile = "+91" + mobile
        message = await client.messages.create(
                        messaging_service_sid=message_sid,
                        body=f"Your Verification Code is {code}",
                        to=mobile
                    )
        # print(message.sid)

        return True
    except Exception as e:
        print(e)
        return "failed"
