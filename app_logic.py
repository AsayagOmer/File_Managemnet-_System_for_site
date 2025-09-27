import os
import sys
from typing import Dict, List, Any, Union, Tuple
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from gspread.exceptions import APIError, WorksheetNotFound
from dotenv import load_dotenv  # NEW: ייבוא ספריית הסודות


# --- Helper function for PyInstaller ---
def resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works for development and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS.
        base_path: str = sys._MEIPASS  # noqa: PyProtectedMember
    except AttributeError:
        base_path: str = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# טוען את משתני הסביבה מקובץ .env מיד בתחילת הרצת הקוד
load_dotenv()


class BackendManager:
    """Manages all backend interactions with Google Drive and Google Sheets."""

    # --- Configuration Constants (READ FROM .ENV) ---
    SCOPES: List[str] = ['https://www.googleapis.com/auth/drive',
                         'https://www.googleapis.com/auth/spreadsheets']
    CREDENTIALS_FILE: str = resource_path('credentials.json')

    # 1. GOOGLE SHEETS ID: נקרא מה-env
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID")

    # 2. Google Drive Folder IDs - נבנה מחדש מתוך המשתנים ב- .env
    COURSE_FOLDER_IDS: Dict[str, Dict[str, str]] = {
        'theory': {
            'curriculum': os.getenv("THEORY_CURRICULUM_ID"),
            'useful-files': os.getenv("THEORY_USEFUL_FILES_ID"),
            'exams-mahat-handasaim': os.getenv("THEORY_EXAMS_MAHAT_HANDASAIM_ID"),
            'exams-mahat-technaim': os.getenv("THEORY_EXAMS_MAHAT_TECHNAIM_ID"),
            'exams-education-handasaim': os.getenv("THEORY_EXAMS_EDUCATION_HANDASAIM_ID"),
            'exams-education-technaim': os.getenv("THEORY_EXAMS_EDUCATION_TECHNAIM_ID"),
            'solutions-mahat-handasaim': os.getenv("THEORY_SOLUTIONS_MAHAT_HANDASAIM_ID"),
            'solutions-mahat-technaim': os.getenv("THEORY_SOLUTIONS_MAHAT_TECHNAIM_ID"),
            'solutions-education-handasaim': os.getenv("THEORY_SOLUTIONS_EDUCATION_HANDASAIM_ID"),
            'solutions-education-technaim': os.getenv("THEORY_SOLUTIONS_EDUCATION_TECHNAIM_ID"),
            'study-materials-handasaim': os.getenv("THEORY_STUDY_MATERIALS_HANDASAIM_ID"),
            'study-materials-technaim': os.getenv("THEORY_STUDY_MATERIALS_TECHNAIM_ID"),
            'practice-mahat-handasaim': os.getenv("THEORY_PRACTICE_MAHAT_HANDASAIM_ID"),
            'practice-mahat-technaim': os.getenv("THEORY_PRACTICE_MAHAT_TECHNAIM_ID"),
            'practice-education-handasaim': os.getenv("THEORY_PRACTICE_EDUCATION_HANDASAIM_ID"),
            'practice-education-technaim': os.getenv("THEORY_PRACTICE_EDUCATION_TECHNAIM_ID"),
        },
        'machines': {
            'curriculum': os.getenv("MACHINES_CURRICULUM_ID"),
            'useful-files': os.getenv("MACHINES_USEFUL_FILES_ID"),
            'exams-mahat-handasaim': os.getenv("MACHINES_EXAMS_MAHAT_HANDASAIM_ID"),
            'exams-mahat-technaim': os.getenv("MACHINES_EXAMS_MAHAT_TECHNAIM_ID"),
            'exams-education-handasaim': os.getenv("MACHINES_EXAMS_EDUCATION_HANDASAIM_ID"),
            'exams-education-technaim': os.getenv("MACHINES_EXAMS_EDUCATION_TECHNAIM_ID"),
            'solutions-mahat-handasaim': os.getenv("MACHINES_SOLUTIONS_MAHAT_HANDASAIM_ID"),
            'solutions-mahat-technaim': os.getenv("MACHINES_SOLUTIONS_MAHAT_TECHNAIM_ID"),
            'solutions-education-handasaim': os.getenv("MACHINES_SOLUTIONS_EDUCATION_HANDASAIM_ID"),
            'solutions-education-technaim': os.getenv("MACHINES_SOLUTIONS_EDUCATION_TECHNAIM_ID"),
            'study-materials-handasaim': os.getenv("MACHINES_STUDY_MATERIALS_HANDASAIM_ID"),
            'study-materials-technaim': os.getenv("MACHINES_STUDY_MATERIALS_TECHNAIM_ID"),
            'practice-mahat-handasaim': os.getenv("MACHINES_PRACTICE_MAHAT_HANDASAIM_ID"),
            'practice-mahat-technaim': os.getenv("MACHINES_PRACTICE_MAHAT_TECHNAIM_ID"),
            'practice-education-handasaim': os.getenv("MACHINES_PRACTICE_EDUCATION_HANDASAIM_ID"),
            'practice-education-technaim': os.getenv("MACHINES_PRACTICE_EDUCATION_TECHNAIM_ID"),
        },
        'power': {
            'curriculum': os.getenv("POWER_CURRICULUM_ID"),
            'useful-files': os.getenv("POWER_USEFUL_FILES_ID"),
            'exams-mahat-handasaim': os.getenv("POWER_EXAMS_MAHAT_HANDASAIM_ID"),
            'exams-mahat-technaim': os.getenv("POWER_EXAMS_MAHAT_TECHNAIM_ID"),
            'exams-education-handasaim': os.getenv("POWER_EXAMS_EDUCATION_HANDASAIM_ID"),
            'exams-education-technaim': os.getenv("POWER_EXAMS_EDUCATION_TECHNAIM_ID"),
            'solutions-mahat-handasaim': os.getenv("POWER_SOLUTIONS_MAHAT_HANDASAIM_ID"),
            'solutions-mahat-technaim': os.getenv("POWER_SOLUTIONS_MAHAT_TECHNAIM_ID"),
            'solutions-education-handasaim': os.getenv("POWER_SOLUTIONS_EDUCATION_HANDASAIM_ID"),
            'solutions-education-technaim': os.getenv("POWER_SOLUTIONS_EDUCATION_TECHNAIM_ID"),
            'study-materials-handasaim': os.getenv("POWER_STUDY_MATERIALS_HANDASAIM_ID"),
            'study-materials-technaim': os.getenv("POWER_STUDY_MATERIALS_TECHNAIM_ID"),
            'practice-mahat-handasaim': os.getenv("POWER_PRACTICE_MAHAT_HANDASAIM_ID"),
            'practice-mahat-technaim': os.getenv("POWER_PRACTICE_MAHAT_TECHNAIM_ID"),
            'practice-education-handasaim': os.getenv("POWER_PRACTICE_EDUCATION_HANDASAIM_ID"),
            'practice-education-technaim': os.getenv("POWER_PRACTICE_EDUCATION_TECHNAIM_ID"),
        }
    }

    # 3. BACKGROUND FOLDER IDS - נקראים מה-env
    BACKGROUND_FOLDER_IDS: Dict[str, str] = {
        'Math': os.getenv("BACKGROUND_MATH_ID"),
        'Physics': os.getenv("BACKGROUND_PHYSICS_ID"),
        'Electricity': os.getenv("BACKGROUND_ELECTRICITY_ID"),
        'Calculator': os.getenv("BACKGROUND_CALCULATOR_ID")
    }

    COURSE_MAP = {"תורת החשמל": "theory", "מכונות חשמל": "machines", "מתקנים ומערכות הספק": "power"}
    TOPIC_MAP = {"רקע מתמטי": "Math", "רקע בפיזיקה": "Physics", "חשמל למתחילים": "Electricity",
                 "שימוש במחשבון": "Calculator"}
    CATEGORY_GROUPS = {
        'useful-files': 'קבצים שימושיים',
        'curriculum': 'תכניות לימוד',
        'exams-mahat': 'מבחנים חיצוניים (מה"ט)',
        'exams-education': 'מבחנים חיצוניים (משרד החינוך)',
        'solutions-mahat': 'פתרונות למבחנים (מה"ט)',
        'solutions-education': 'פתרונות למבחנים (משרד החינוך)',
        'study-materials': 'חומרי לימוד',
        'practice-mahat': 'שאלות לתרגול (מה"ט)',
        'practice-education': 'שאלות לתרגול (משרד החינוך)',
    }

    def __init__(self):
        """Initializes the backend manager by authenticating with Google APIs."""
        # בדיקה קריטית: ודא שכל המזהים נטענו, במיוחד ה-SPREADSHEET_ID
        if not self.SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID not loaded. Check your .env file.")

        self.drive_service, self.gc, self.error = self._authenticate_google()

    def _authenticate_google(self) -> Tuple[Any, Any, Union[str, None]]:
        """Authenticates and returns the Google service objects."""
        creds: Union[Credentials, None] = None
        token_path = resource_path('token.json')
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                except FileNotFoundError:
                    return None, None, "קובץ credentials.json לא נמצא. נא וודא שהקובץ קיים באותה תיקייה של הקובץ ההרצה."
                except Exception as e:
                    return None, None, f"שגיאת אימות: {e}"
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            drive_service = build('drive', 'v3', credentials=creds)
            gc = gspread.authorize(creds)
            return drive_service, gc, None
        except Exception as e:
            return None, None, f"שגיאת חיבור ל-Google API: {e}"

    def upload_file_to_drive(self, file_path: str, folder_id: str) -> Tuple[
        Union[str, None], Union[str, None], Union[str, None]]:
        """
        Uploads a file to a specific Google Drive folder and makes it public.
        """
        if not self.drive_service:
            return None, None, "שירות Google Drive לא זמין."
        if not folder_id:
            return None, None, "מזהה התיקייה ריק או לא תקין."

        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink').execute()

            permission = {'type': 'anyone', 'role': 'reader'}
            self.drive_service.permissions().create(
                fileId=file.get('id'),
                body=permission,
                fields='id').execute()

            file_id: str = file.get('id')
            file_url: str = file.get('webViewLink')
            return file_id, file_url, None
        except Exception as e:
            return None, None, f"אירעה שגיאה בהעלאת הקובץ: {e}"

    def delete_file_from_drive(self, file_id: str) -> Union[bool, str]:
        """Deletes a file from Google Drive."""
        if not self.drive_service:
            return "שירות Google Drive לא זמין."
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            return f"אירעה שגיאה במחיקת הקובץ מ-Drive: {e}"

    def update_google_sheet(self, sheet_name: str, data: List[Any]) -> Union[bool, str]:
        """Updates the specified Google Sheet with new data."""
        if not self.gc:
            return "שירות Google Sheets לא זמין."
        try:
            worksheet = self.gc.open_by_key(self.SPREADSHEET_ID).worksheet(sheet_name)
            worksheet.append_row(data)
            return True
        except APIError as e:
            return f"כשל בעדכון גיליון הנתונים: {e}"
        except Exception as e:
            return f"אירעה שגיאה בעדכון גיליון הנתונים: {e}"

    def find_record_in_sheet(self, sheet_name: str, search_string: str) -> Tuple[
        Union[List[str], None], int]:
        """Finds a record in a sheet based on a search string."""
        if not self.gc:
            return None, -1
        try:
            worksheet = self.gc.open_by_key(self.SPREADSHEET_ID).worksheet(sheet_name)
            all_records = worksheet.get_all_values()

            for i, record in enumerate(all_records):
                if sheet_name == 'background' and len(record) > 1 and search_string in record[1]:
                    return record, i + 1
                elif sheet_name == 'courses' and len(record) > 0 and search_string in record[0]:
                    return record, i + 1
            return None, -1
        except Exception:
            return None, -1

    def delete_row_from_sheet(self, sheet_name: str, row_index: int) -> Union[bool, str]:
        """Deletes a row from the specified Google Sheet."""
        if not self.gc:
            return "שירות Google Sheets לא זמין."
        try:
            worksheet = self.gc.open_by_key(self.SPREADSHEET_ID).worksheet(sheet_name)
            worksheet.delete_rows(row_index)
            return True
        except WorksheetNotFound:
            return f"הגיליון '{sheet_name}' לא נמצא."
        except Exception as e:
            return f"אירעה שגיאה במחיקת השורה מהגיליון: {e}"

    @staticmethod
    def get_youtube_embed_url(video_url: str) -> str:
        """Converts a standard YouTube URL to an embed URL."""
        try:
            video_id = video_url.split("v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        except IndexError:
            return video_url


# Re-exporting for compatibility with existing imports
COURSE_MAP = BackendManager.COURSE_MAP
TOPIC_MAP = BackendManager.TOPIC_MAP
CATEGORY_GROUPS = BackendManager.CATEGORY_GROUPS