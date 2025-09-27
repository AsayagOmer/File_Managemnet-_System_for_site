import unittest
from unittest.mock import patch
import tkinter as tk

# Ensure the uploader_app.py file is available in the same directory
from uploader_app import UploaderApp


class TestUploaderAppLogic(unittest.TestCase):

    def setUp(self):
        """
        Setup: Creates the Tkinter root and the UploaderApp instance,
        mocking a successful connection to the BackendManager.
        This isolates the UI logic from actual Google API calls.
        """
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the Tkinter window during testing

        # Mock the BackendManager class to prevent actual database/API calls
        with patch('uploader_app.BackendManager', autospec=True) as MockBackendManager:
            self.app = UploaderApp(self.root)
            self.app.backend = MockBackendManager.return_value
            self.app.backend.error = None

            # Set up mock mapping data, as if loaded successfully from the Backend
            self.app.backend.COURSE_MAP = {"תורת החשמל": "theory"}
            self.app.backend.CATEGORY_GROUPS = {
                'useful-files': 'קבצים שימושיים',
                'exams-mahat': 'מבחנים חיצוניים (מה"ט)'
            }
            self.app.backend.COURSE_FOLDER_IDS = {
                'theory': {
                    'useful-files': 'test_folder_id_1',
                    'exams-mahat-handasaim': 'test_folder_id_2'
                }
            }

        # Run UI setup to ensure all widgets and variables are initialized
        self.app._setup_ui_elements()

    def tearDown(self):
        """
        Cleanup: Destroys the Tkinter root window after each test.
        """
        self.root.destroy()

    # ------------------------------------------------------------------
    # UPLOAD TEST: Verifies the fix for Column F (data list length = 4)
    # ------------------------------------------------------------------
    @patch('uploader_app.messagebox')
    @patch('os.path.basename', return_value='test_file.pdf')
    def test_upload_course_file_data_structure_is_4_items(self, mock_basename, mock_messagebox):
        """
        Tests that course file upload generates a data list of **exactly 4 items** for the 'courses' sheet, confirming the file_ID (previously in column F)
        is successfully excluded.
        """
        # 1. Setup Test Input for a successful file upload flow.
        self.app.main_action_var.set('upload')
        self.app.main_category_var.set("קורסים")
        self.app.course_var.set("תורת החשמל")
        self.app.subcategory_group_var.set("קבצים שימושיים")
        self.app.file_path = '/fake/path/to/test_file.pdf'
        self.app.upload_widgets['file_title_entry'].delete(0, tk.END)
        self.app.upload_widgets['file_title_entry'].insert(0, 'כותרת קובץ בדיקה')

        # 2. Mock successful file upload and sheet update responses.
        fake_file_id = 'FAKE_FILE_ID_123'
        fake_file_url = 'https://drive.google.com/test_url'
        # The upload function returns (file_id, file_url, error)
        self.app.backend.upload_file_to_drive.return_value = (fake_file_id, fake_file_url, None)
        self.app.backend.update_google_sheet.return_value = True

        # 3. Execute the function under test.
        self.app._handle_course_upload()

        # 4. Assertions.
        self.app.backend.update_google_sheet.assert_called_once()
        sheet_name, actual_data = self.app.backend.update_google_sheet.call_args[0]

        # Expected data: [Title, URL, subcategory_key, course_key] (4 items)
        expected_data = ['כותרת קובץ בדיקה', fake_file_url, 'useful-files', 'theory']

        self.assertEqual(sheet_name, 'courses', "Sheet name must be 'courses'")
        self.assertEqual(len(actual_data), 4,
                         f"Data list must be length 4 (no file ID), but found length {len(actual_data)}")
        self.assertEqual(actual_data, expected_data,
                         "The row data does not match the expected structure.")

    # ------------------------------------------------------------------
    # DELETION TEST: Verifies the logic correctly identifies and removes
    # a Drive file and the sheet record.
    # ------------------------------------------------------------------
    @patch('uploader_app.messagebox')
    def test_delete_content_file_success(self, mock_messagebox):
        """
        Tests the complete deletion flow for a Google Drive file, ensuring
        it deletes from both Drive and the Google Sheet using the correct ID and row index.
        """
        # 1. Setup Test Input.
        self.app.main_category_var.set("קורסים")
        self.app.delete_name_var.set("כותרת קובץ לבדיקה")

        # Simulate a found record (Row 2 in the sheet, index 1)
        # Record Structure for 'courses' (4 columns): [Title, URL, Subcategory, Course]
        fake_file_id = 'fake_drive_id_to_delete'
        # The application must extract the ID from this URL
        fake_drive_url = f'https://drive.google.com/file/d/{fake_file_id}/view'
        mock_record = ['כותרת קובץ לבדיקה', fake_drive_url, 'useful-files', 'theory']
        row_index = 2  # The actual row number in the Google Sheet (1-indexed)

        # 2. Mock API call results.
        # find_record_in_sheet returns (record_list, row_index)
        self.app.backend.find_record_in_sheet.return_value = (mock_record, row_index)
        self.app.backend.delete_file_from_drive.return_value = True
        self.app.backend.delete_row_from_sheet.return_value = True

        # Mock user clicking 'Yes' to confirm deletion.
        mock_messagebox.askyesno.return_value = True

        # 3. Execute the function under test.
        self.app._delete_content()

        # 4. Assertions.

        # Verify the file ID is correctly extracted from the URL and passed to the Drive API.
        self.app.backend.delete_file_from_drive.assert_called_once_with(fake_file_id)

        # Verify the sheet deletion was called using the correct row index.
        self.app.backend.delete_row_from_sheet.assert_called_once_with('courses', row_index)


if __name__ == '__main__':
    unittest.main()
