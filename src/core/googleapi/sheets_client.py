import os
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import GoogleAPIError

from ..shared.exceptions import ExternalServiceError

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_client():
    """Get authenticted Google Sheets client."""
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    if not service_account_file or not os.path.exists(service_account_file):
        raise ExternalServiceError(
            detail='Google service account file not found',
            context={'file': service_account_file}
        )

    creds = Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)
