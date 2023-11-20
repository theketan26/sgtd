from os import path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import FastAPI

app = FastAPI()
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = None

    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
            creds = flow.run_local_server(port = 0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials = creds)

        now = dt.datetime.now().isoformat() + 'Z'

        events_result = service.events().list(
            calendarId = 'primary',
            timeMin = now,
            maxResults = 10,
            singleEvents = True,
            orderBy = 'startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            print("no event")

        else:
            for event in events:
                print(event['summary'])

    except HttpError as err:
        print(err)


@app.get('/')
async def root():
    main()
    return {
        'message': 'This is working'
    }
