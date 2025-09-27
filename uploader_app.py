import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from typing import Dict, List, Any, Union
from app_logic import BackendManager


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works for development and for PyInstaller.
    """
    try:
        base_path: str = sys._MEIPASS
    except AttributeError:
        base_path: str = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class UploaderApp:
    def __init__(self, main_window: tk.Tk) -> None:
        self.main_window: tk.Tk = main_window
        self.main_window.title("מערכת העלאת ומחיקת קבצים")
        self.main_window.geometry("800x600")

        self.backend = None
        self.file_path: Union[str, None] = None
        self.file_id: Union[str, None] = None

        self.main_action_var = tk.StringVar(value='upload')
        self.main_category_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.topic_var = tk.StringVar()
        self.subcategory_group_var = tk.StringVar()
        self.final_subcategory_var = tk.StringVar()
        self.content_type_var = tk.StringVar(value='file')

        self.delete_content_type_var = tk.StringVar(value='file')
        self.delete_name_var = tk.StringVar()

        self.main_frame: Union[ttk.Frame, None] = None
        self.action_frame: Union[ttk.Frame, None] = None
        self.action_button: Union[ttk.Button, None] = None
        self.upload_widgets: Dict[str, Union[ttk.Widget, None]] = {}
        self.delete_widgets: Dict[str, Union[ttk.Widget, None]] = {}

        self.auth_info_label = ttk.Label(self.main_window, text="מתחבר לחשבון Google...",
                                         font=("Helvetica", 10, "italic"))
        self.auth_info_label.place(relx=0.5, rely=0.95, anchor='s')

        self.main_window.after(100, self._start_auth)

    def _start_auth(self) -> None:
        self.backend = BackendManager()
        if self.backend.error:
            self.auth_info_label.config(text=self.backend.error, foreground="red")
        else:
            self.auth_info_label.config(text="התחברות לחשבון Google הצליחה!", foreground="green")
            self._setup_ui_elements()

    def _setup_ui_elements(self) -> None:
        """Helper method to create all UI widgets."""
        self.main_frame = ttk.Frame(self.main_window, padding="20")
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        ttk.Label(self.main_frame, text="מערכת העלאת ומחיקת תוכן", font=("Helvetica", 20, "bold")).pack(pady=20)

        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.pack(pady=10)
        ttk.Radiobutton(self.action_frame, text="העלאת תוכן", variable=self.main_action_var, value='upload').pack(
            side='right', padx=10)
        ttk.Radiobutton(self.action_frame, text="מחיקת תוכן", variable=self.main_action_var, value='delete').pack(
            side='right', padx=10)

        self.action_button = ttk.Button(self.action_frame, text="אישור", command=self._show_selected_action_frame)
        self.action_button.pack(pady=10)

        self._setup_upload_ui()
        self._setup_delete_ui()

    def _setup_upload_ui(self) -> None:
        """Sets up all UI widgets for the upload functionality."""
        upload_frame = ttk.Frame(self.main_frame)

        self.upload_widgets['main_category_label'] = ttk.Label(upload_frame, text=":קטגוריה ראשית",
                                                               font=("Helvetica", 14))
        self.upload_widgets['main_category_combo'] = ttk.Combobox(upload_frame, textvariable=self.main_category_var,
                                                                  state="readonly",
                                                                  values=["קורסים", "רקע להנדסאים"])
        self.upload_widgets['main_category_combo'].bind("<<ComboboxSelected>>", self._update_upload_options)

        self.upload_widgets['course_label'] = ttk.Label(upload_frame, text=":בחירת קורס", font=("Helvetica", 14))
        self.upload_widgets['course_combo'] = ttk.Combobox(upload_frame, textvariable=self.course_var, state="readonly",
                                                           values=list(self.backend.COURSE_MAP.keys()))
        self.upload_widgets['course_combo'].bind("<<ComboboxSelected>>", self._update_subcategories_upload)

        self.upload_widgets['topic_label'] = ttk.Label(upload_frame, text=":בחירת נושא", font=("Helvetica", 14))
        self.upload_widgets['topic_combo'] = ttk.Combobox(upload_frame, textvariable=self.topic_var, state="readonly",
                                                          values=list(self.backend.TOPIC_MAP.keys()))
        self.upload_widgets['topic_combo'].bind("<<ComboboxSelected>>", self._show_upload_form)

        self.upload_widgets['subcategory_group_label'] = ttk.Label(upload_frame, text=":בחירת קבוצת קטגוריות",
                                                                   font=("Helvetica", 14))
        self.upload_widgets['subcategory_group_combo'] = ttk.Combobox(upload_frame,
                                                                      textvariable=self.subcategory_group_var,
                                                                      state="readonly",
                                                                      values=list(
                                                                          self.backend.CATEGORY_GROUPS.values()),
                                                                      width=40)
        self.upload_widgets['subcategory_group_combo'].bind("<<ComboboxSelected>>",
                                                            self._update_final_subcategory_upload)

        self.upload_widgets['final_subcategory_label'] = ttk.Label(upload_frame, text=":בחירת תת-קטגוריה",
                                                                   font=("Helvetica", 14))
        self.upload_widgets['final_subcategory_combo'] = ttk.Combobox(upload_frame,
                                                                      textvariable=self.final_subcategory_var,
                                                                      state="readonly", width=40)
        self.upload_widgets['final_subcategory_combo'].bind("<<ComboboxSelected>>", self._show_upload_form)

        # =====trial=====
        # upload_type_frame = ttk.LabelFrame(tab, text="סוג התוכן")
        # upload_type_frame.pack(padx=20, pady=10, fill="x")
        #
        # # כפתורי רדיו לבחירת סוג - משתמשים ב-side='right'
        # # ארזנו את "קישור חיצוני" קודם כדי שיבוא משמאל ל"קובץ" באריזה מימין לימין (RTL)
        # link_radio = ttk.Radiobutton(upload_type_frame, text="קישור חיצוני", variable=self.upload_type_var,
        #                              value='external_link', command=self._toggle_upload_fields)
        # link_radio.pack(side="right", padx=10, pady=5)
        #
        # local_radio = ttk.Radiobutton(upload_type_frame, text="קובץ", variable=self.upload_type_var, value='local_file',
        #                               command=self._toggle_upload_fields)
        # local_radio.pack(side="right", padx=10, pady=5)
        # # -------------------------------
        #
        # # פריים לבחירת קובץ או קישור (זה מגיע אחרי הבחירה ומשתנה בהתאם)
        # self.file_input_frame = ttk.LabelFrame(tab, text="קובץ / קישור")
        #================

        self.upload_widgets['type_frame'] = ttk.Frame(upload_frame)
        ttk.Radiobutton(self.upload_widgets['type_frame'], text="העלאת קובץ", variable=self.content_type_var,
                        value='file',
                        command=self._update_upload_form).pack(side='right', padx=10)
        ttk.Radiobutton(self.upload_widgets['type_frame'], text="העלאת קישור ליוטיוב", variable=self.content_type_var,
                        value='video',
                        command=self._update_upload_form).pack(side='right', padx=10)

        self.upload_widgets['upload_frame'] = ttk.Frame(upload_frame, padding="10")
        self.upload_widgets['video_url_label'] = ttk.Label(self.upload_widgets['upload_frame'], text=":קישור ליוטיוב")
        self.upload_widgets['video_url_entry'] = ttk.Entry(self.upload_widgets['upload_frame'], width=40)
        self.upload_widgets['video_title_label'] = ttk.Label(self.upload_widgets['upload_frame'], text=":כותרת הסרטון")
        self.upload_widgets['video_title_entry'] = ttk.Entry(self.upload_widgets['upload_frame'], width=40)
        self.upload_widgets['video_desc_label'] = ttk.Label(self.upload_widgets['upload_frame'], text=":תיאור קצר")
        self.upload_widgets['video_desc_entry'] = ttk.Entry(self.upload_widgets['upload_frame'], width=40)
        self.upload_widgets['file_title_label'] = ttk.Label(self.upload_widgets['upload_frame'], text=":שם הקובץ")
        self.upload_widgets['file_title_entry'] = ttk.Entry(self.upload_widgets['upload_frame'], width=40)
        self.upload_widgets['file_path_label'] = ttk.Label(self.upload_widgets['upload_frame'],
                                                           text="נתיב קובץ: לא נבחר קובץ")
        self.upload_widgets['browse_button'] = ttk.Button(self.upload_widgets['upload_frame'], text="...בחר קובץ",
                                                          command=self._browse_file)
        self.upload_widgets['upload_button'] = ttk.Button(self.upload_widgets['upload_frame'], text="העלה תוכן",
                                                          command=self._upload_content)

        self.upload_widgets['upload_main_frame'] = upload_frame

    def _setup_delete_ui(self) -> None:
        """Sets up all UI widgets for the delete functionality."""
        delete_frame = ttk.Frame(self.main_frame)

        self.delete_widgets['main_category_label'] = ttk.Label(delete_frame, text=":קטגוריה ראשית",
                                                               font=("Helvetica", 14))
        self.delete_widgets['main_category_combo'] = ttk.Combobox(delete_frame, textvariable=self.main_category_var,
                                                                  state="readonly",
                                                                  values=["קורסים", "רקע להנדסאים"])
        self.delete_widgets['main_category_combo'].bind("<<ComboboxSelected>>", self._update_delete_options)

        self.delete_widgets['course_label'] = ttk.Label(delete_frame, text=":בחירת קורס", font=("Helvetica", 14))
        self.delete_widgets['course_combo'] = ttk.Combobox(delete_frame, textvariable=self.course_var, state="readonly",
                                                           values=list(self.backend.COURSE_MAP.keys()))
        self.delete_widgets['course_combo'].bind("<<ComboboxSelected>>", self._update_subcategories_delete)

        self.delete_widgets['topic_label'] = ttk.Label(delete_frame, text=":בחירת נושא", font=("Helvetica", 14))
        self.delete_widgets['topic_combo'] = ttk.Combobox(delete_frame, textvariable=self.topic_var, state="readonly",
                                                          values=list(self.backend.TOPIC_MAP.keys()))
        self.delete_widgets['topic_combo'].bind("<<ComboboxSelected>>", self._show_delete_form)

        self.delete_widgets['subcategory_group_label'] = ttk.Label(delete_frame, text=":בחירת קבוצת קטגוריות",
                                                                   font=("Helvetica", 14))
        self.delete_widgets['subcategory_group_combo'] = ttk.Combobox(delete_frame,
                                                                      textvariable=self.subcategory_group_var,
                                                                      state="readonly",
                                                                      values=list(
                                                                          self.backend.CATEGORY_GROUPS.values()),
                                                                      width=40)
        self.delete_widgets['subcategory_group_combo'].bind("<<ComboboxSelected>>",
                                                            self._update_final_subcategory_delete)

        self.delete_widgets['final_subcategory_label'] = ttk.Label(delete_frame, text=":בחירת תת-קטגוריה",
                                                                   font=("Helvetica", 14))
        self.delete_widgets['final_subcategory_combo'] = ttk.Combobox(delete_frame,
                                                                      textvariable=self.final_subcategory_var,
                                                                      state="readonly", width=40)
        self.delete_widgets['final_subcategory_combo'].bind("<<ComboboxSelected>>", self._show_delete_form)

        self.delete_widgets['type_frame'] = ttk.Frame(delete_frame)
        ttk.Radiobutton(self.delete_widgets['type_frame'], text="מחק קובץ", variable=self.delete_content_type_var,
                        value='file',
                        command=self._show_delete_form).pack(side='right', padx=10)
        ttk.Radiobutton(self.delete_widgets['type_frame'], text="מחק קישור ליוטיוב",
                        variable=self.delete_content_type_var, value='video',
                        command=self._show_delete_form).pack(side='right', padx=10)

        self.delete_widgets['delete_form_frame'] = ttk.Frame(delete_frame, padding="10")
        self.delete_widgets['delete_name_label'] = ttk.Label(self.delete_widgets['delete_form_frame'],
                                                             text=":הכנס שם קובץ או סרטון למחיקה",
                                                             font=("Helvetica", 14))
        self.delete_widgets['delete_name_entry'] = ttk.Entry(self.delete_widgets['delete_form_frame'],
                                                             textvariable=self.delete_name_var, width=50)
        self.delete_widgets['delete_button'] = ttk.Button(self.delete_widgets['delete_form_frame'], text="מחק תוכן",
                                                          command=self._delete_content)

        self.delete_widgets['delete_main_frame'] = delete_frame

    def _show_selected_action_frame(self) -> None:
        """Switches between the upload and delete UI frames."""
        action: str = self.main_action_var.get()
        self.upload_widgets['upload_main_frame'].pack_forget()
        self.delete_widgets['delete_main_frame'].pack_forget()
        self._reset_delete_form()
        self._reset_upload_form()

        if action == 'upload':
            self.upload_widgets['upload_main_frame'].pack()
            self.upload_widgets['main_category_label'].pack(pady=(10, 0))
            self.upload_widgets['main_category_combo'].pack(pady=5)
            self._update_upload_options(None)
        elif action == 'delete':
            self.delete_widgets['delete_main_frame'].pack()
            self.delete_widgets['main_category_label'].pack(pady=(10, 0))
            self.delete_widgets['main_category_combo'].pack(pady=5)
            self._update_delete_options(None)

    def _update_upload_options(self, _: Any) -> None:
        """Updates the UI based on the main category selection for upload."""
        for widget in ['course_label', 'course_combo', 'topic_label', 'topic_combo',
                       'subcategory_group_label', 'subcategory_group_combo',
                       'final_subcategory_label', 'final_subcategory_combo',
                       'type_frame', 'upload_frame']:
            if self.upload_widgets[widget] is not None:
                self.upload_widgets[widget].pack_forget()

        selected_category: str = self.main_category_var.get()
        if selected_category == "קורסים":
            self.upload_widgets['course_label'].pack(pady=(10, 0))
            self.upload_widgets['course_combo'].pack(pady=5)
        elif selected_category == "רקע להנדסאים":
            self.upload_widgets['topic_label'].pack(pady=(10, 0))
            self.upload_widgets['topic_combo'].pack(pady=5)
            self.upload_widgets['type_frame'].pack(pady=10)
            self._update_upload_form()

    def _update_subcategories_upload(self, _: Any) -> None:
        """Updates subcategory combobox for upload based on selected course."""
        self.upload_widgets['subcategory_group_label'].pack(pady=(10, 0))
        self.upload_widgets['subcategory_group_combo'].pack(pady=5)
        self.upload_widgets['final_subcategory_label'].pack_forget()
        self.upload_widgets['final_subcategory_combo'].pack_forget()
        self.upload_widgets['upload_frame'].pack_forget()
        self.upload_widgets['subcategory_group_combo']['values'] = list(self.backend.CATEGORY_GROUPS.values())
        self.subcategory_group_var.set('')

    def _update_final_subcategory_upload(self, _: Any) -> None:
        """Updates final subcategory combobox for upload based on selected group."""
        selected_group: str = self.subcategory_group_var.get()
        group_keys = [key for key, value in self.backend.CATEGORY_GROUPS.items() if value == selected_group]
        group_key = group_keys[0] if group_keys else None

        if group_key in ['useful-files', 'curriculum']:
            self.upload_widgets['final_subcategory_label'].pack_forget()
            self.upload_widgets['final_subcategory_combo'].pack_forget()
            self.upload_widgets['upload_frame'].pack_forget()
            self._show_upload_form()
        else:
            self.upload_widgets['final_subcategory_label'].pack(pady=(10, 0))
            self.upload_widgets['final_subcategory_combo'].pack(pady=5)
            self.upload_widgets['upload_frame'].pack_forget()
            self.upload_widgets['final_subcategory_combo']['values'] = ['הנדסאים', 'טכנאים']
            self.final_subcategory_var.set('')
            self._update_upload_form()

    def _show_upload_form(self, _: Any = None) -> None:
        """Shows the upload form and sets content type."""
        if self.main_category_var.get() == "קורסים":
            self.content_type_var.set('file')
            self.upload_widgets['type_frame'].pack_forget()
        else:
            self.upload_widgets['type_frame'].pack(pady=10)

        self.upload_widgets['upload_frame'].pack(pady=10)
        self._update_upload_form()

    def _update_upload_form(self) -> None:
        """Toggles between file and video upload widgets."""
        for widget in self.upload_widgets['upload_frame'].winfo_children():
            widget.pack_forget()

        content_type: str = self.content_type_var.get()
        if content_type == 'file':
            self.upload_widgets['file_title_label'].pack(pady=5)
            self.upload_widgets['file_title_entry'].pack(pady=5)
            self.upload_widgets['file_path_label'].pack(pady=5)
            self.upload_widgets['browse_button'].pack(pady=5)
            self.upload_widgets['upload_button'].pack(pady=10)
        elif content_type == 'video':
            self.upload_widgets['video_url_label'].pack(pady=5)
            self.upload_widgets['video_url_entry'].pack(pady=5)
            self.upload_widgets['video_title_label'].pack(pady=5)
            self.upload_widgets['video_title_entry'].pack(pady=5)
            self.upload_widgets['video_desc_label'].pack(pady=5)
            self.upload_widgets['video_desc_entry'].pack(pady=5)
            self.upload_widgets['upload_button'].pack(pady=10)

    def _browse_file(self) -> None:
        """Opens a file dialog for the user to select a file."""
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.upload_widgets['file_path_label'].config(text=f"נתיב קובץ: {self.file_path}")
            self.upload_widgets['file_title_entry'].delete(0, tk.END)
            self.upload_widgets['file_title_entry'].insert(0, os.path.basename(self.file_path))

    def _upload_content(self) -> None:
        """Handles the upload logic for both files and videos."""
        main_category: str = self.main_category_var.get()
        content_type: str = self.content_type_var.get()

        if self.backend is None or self.backend.drive_service is None or self.backend.gc is None:
            messagebox.showerror("שגיאה", "שגיאת אימות. נא וודא שקובצי האימות קיימים.")
            return

        if main_category == "קורסים":
            self._handle_course_upload()
        elif main_category == "רקע להנדסאים":
            self._handle_background_upload(content_type)

    def _handle_course_upload(self) -> None:
        """Handles the logic for course-related uploads."""
        course_key: str = self.backend.COURSE_MAP.get(self.course_var.get().strip(), "")
        selected_group_name: str = self.subcategory_group_var.get().strip()
        selected_final_name: str = self.final_subcategory_var.get().strip()

        group_keys = [key for key, value in self.backend.CATEGORY_GROUPS.items() if value == selected_group_name]
        group_key = group_keys[0] if group_keys else None

        if not group_key:
            messagebox.showerror("שגיאה", "נא בחר קבוצת קטגוריות.")
            return

        # Correct logic to determine the subcategory key
        if group_key in ['useful-files', 'curriculum']:
            subcategory_key = group_key
        else:
            if not selected_final_name:
                messagebox.showerror("שגיאה", "נא בחר תת-קטגוריה ('הנדסאים' או 'טכנאים').")
                return
            final_key = 'handasaim' if selected_final_name == 'הנדסאים' else 'technaim'
            subcategory_key = f"{group_key}-{final_key}"

        if not all([course_key, subcategory_key, self.file_path]):
            messagebox.showerror("שגיאה", "נא בחר קורס, קטגוריה וקובץ.")
            return

        file_title: str = self.upload_widgets['file_title_entry'].get().strip()
        if not file_title:
            messagebox.showerror("שגיאה", "נא הכנס שם לקובץ.")
            return

        folder_id = self.backend.COURSE_FOLDER_IDS.get(course_key, {}).get(subcategory_key, "")
        if not folder_id:
            messagebox.showerror("שגיאה", f"לא נמצאה תיקייה מתאימה עבור '{selected_group_name}'.")
            return

        file_id, file_url, error = self.backend.upload_file_to_drive(self.file_path, folder_id)

        if error:
            messagebox.showerror("שגיאת העלאה", error)
        else:
            # --- השינוי שבוצע ---
            # Remove file_id from the data list for 'courses' sheet
            data: List[Any] = [file_title, file_url, subcategory_key, course_key]
            # --------------------
            sheet_update_result = self.backend.update_google_sheet('courses', data)
            if sheet_update_result is True:
                messagebox.showinfo("עדכון גיליון", "גיליון הנתונים עודכן בהצלחה!")
            else:
                messagebox.showerror("שגיאת עדכון", sheet_update_result)
        self._reset_upload_form()

    def _handle_background_upload(self, content_type: str) -> None:
        """Handles the logic for background-related uploads."""
        topic_key: str = self.backend.TOPIC_MAP.get(self.topic_var.get(), "")

        if not topic_key:
            messagebox.showerror("שגיאה", "נא בחר נושא.")
            return

        if content_type == 'file':
            if not self.file_path:
                messagebox.showerror("שגיאה", "נא בחר קובץ להעלאה.")
                return
            file_title: str = self.upload_widgets['file_title_entry'].get().strip()
            if not file_title:
                messagebox.showerror("שגיאה", "נא הכנס שם לקובץ.")
                return

            file_id, content_url, error = self.backend.upload_file_to_drive(self.file_path,
                                                                            self.backend.BACKGROUND_FOLDER_IDS[
                                                                                topic_key])
            if error:
                messagebox.showerror("שגיאת העלאה", error)
            else:
                data: List[Any] = ['file', file_title, "", content_url, topic_key]
                sheet_update_result = self.backend.update_google_sheet('background', data)
                if sheet_update_result is True:
                    messagebox.showinfo("עדכון גיליון", "גיליון הנתונים עודכן בהצלחה!")
                else:
                    messagebox.showerror("שגיאת עדכון", sheet_update_result)

        elif content_type == 'video':
            video_url: str = self.upload_widgets['video_url_entry'].get().strip()
            video_title: str = self.upload_widgets['video_title_entry'].get().strip()
            video_description: str = self.upload_widgets['video_desc_entry'].get().strip()

            if not video_url or not video_title:
                messagebox.showerror("שגיאה", "נא הכנס קישור וכותרת לסרטון.")
                return

            content_url: str = self.backend.get_youtube_embed_url(video_url)
            data: List[Any] = ['video', video_title, video_description, content_url, topic_key]
            sheet_update_result = self.backend.update_google_sheet('background', data)
            if sheet_update_result is True:
                messagebox.showinfo("עדכון גיליון", "גיליון הנתונים עודכן בהצלחה!")
            else:
                messagebox.showerror("שגיאת עדכון", sheet_update_result)

        self._reset_upload_form()

    def _reset_upload_form(self) -> None:
        """Resets the upload form to its initial state."""
        self.main_category_var.set('')
        self.course_var.set('')
        self.topic_var.set('')
        self.subcategory_group_var.set('')
        self.final_subcategory_var.set('')
        self.upload_widgets['file_title_entry'].delete(0, tk.END)
        self.upload_widgets['video_url_entry'].delete(0, tk.END)
        self.upload_widgets['video_title_entry'].delete(0, tk.END)
        self.upload_widgets['video_desc_entry'].delete(0, tk.END)
        self.upload_widgets['file_path_label'].config(text="נתיב קובץ: לא נבחר קובץ")

    def _update_delete_options(self, _: Any) -> None:
        """Updates the UI based on the main category selection for delete."""
        for widget in ['course_label', 'course_combo', 'topic_label', 'topic_combo',
                       'subcategory_group_label', 'subcategory_group_combo',
                       'final_subcategory_label', 'final_subcategory_combo',
                       'type_frame', 'delete_form_frame']:
            if self.delete_widgets[widget] is not None:
                self.delete_widgets[widget].pack_forget()

        selected_category: str = self.main_category_var.get()
        if selected_category == "קורסים":
            self.delete_widgets['course_label'].pack(pady=(10, 0))
            self.delete_widgets['course_combo'].pack(pady=5)
        elif selected_category == "רקע להנדסאים":
            self.delete_widgets['topic_label'].pack(pady=(10, 0))
            self.delete_widgets['topic_combo'].pack(pady=5)
            self.delete_widgets['type_frame'].pack(pady=10)
            self._show_delete_form()

    def _update_subcategories_delete(self, _: Any) -> None:
        """Updates subcategory combobox for delete based on selected course."""
        self.delete_widgets['subcategory_group_label'].pack(pady=(10, 0))
        self.delete_widgets['subcategory_group_combo'].pack(pady=5)
        self.delete_widgets['final_subcategory_label'].pack_forget()
        self.delete_widgets['final_subcategory_combo'].pack_forget()
        self.delete_widgets['delete_form_frame'].pack_forget()
        self.delete_widgets['subcategory_group_combo']['values'] = list(self.backend.CATEGORY_GROUPS.values())
        self.subcategory_group_var.set('')

    def _update_final_subcategory_delete(self, _: Any) -> None:
        """Updates final subcategory combobox for delete based on selected group."""
        selected_group: str = self.subcategory_group_var.get()
        group_keys = [key for key, value in self.backend.CATEGORY_GROUPS.items() if value == selected_group]
        group_key = group_keys[0] if group_keys else None

        if group_key in ['useful-files', 'curriculum']:
            self.delete_widgets['final_subcategory_label'].pack_forget()
            self.delete_widgets['final_subcategory_combo'].pack_forget()
            self.delete_widgets['delete_form_frame'].pack_forget()
            self._show_delete_form()
        else:
            self.delete_widgets['final_subcategory_label'].pack(pady=(10, 0))
            self.delete_widgets['final_subcategory_combo'].pack(pady=5)
            self.delete_widgets['delete_form_frame'].pack_forget()
            self.delete_widgets['final_subcategory_combo']['values'] = ['הנדסאים', 'טכנאים']
            self.final_subcategory_var.set('')
            self._show_delete_form()

    def _show_delete_form(self, _: Any = None) -> None:
        """Shows the delete form for file name entry."""
        if self.main_category_var.get() == "קורסים":
            self.delete_widgets['type_frame'].pack(pady=10)
        self.delete_widgets['delete_form_frame'].pack(pady=10, fill="x")
        self.delete_widgets['delete_name_label'].pack(pady=5)
        self.delete_widgets['delete_name_entry'].pack(pady=5)
        self.delete_widgets['delete_button'].pack(pady=10)

    def _delete_content(self) -> None:
        """
        Deletes the selected content from the Google Sheet and Google Drive if it's a file.
        """
        content_name_to_delete = self.delete_name_var.get().strip()
        if not content_name_to_delete:
            messagebox.showerror("שגיאה", "אנא הכנס שם של תוכן למחיקה.")
            return

        confirm_delete = messagebox.askyesno(
            "אישור מחיקה", f"האם אתה בטוח שברצונך למחוק רשומה שמכילה את '{content_name_to_delete}'?")
        if not confirm_delete:
            return

        main_category = self.main_category_var.get()
        sheet_name = ""

        if main_category == "קורסים":
            sheet_name = 'courses'
        elif main_category == "רקע להנדסאים":
            sheet_name = 'background'

        if not sheet_name:
            messagebox.showerror("שגיאה", "אנא בחר קטגוריה ראשית.")
            return

        try:
            record_to_delete, row_index = self.backend.find_record_in_sheet(sheet_name, content_name_to_delete)

            if record_to_delete:
                file_id_or_url = ""
                # --- השינוי שבוצע ---
                # Check the URL column for the file ID
                if sheet_name == 'courses' and len(record_to_delete) > 1:
                    file_id_or_url = record_to_delete[1]
                elif sheet_name == 'background' and len(record_to_delete) > 3:
                    file_id_or_url = record_to_delete[3]
                # --------------------

                if not file_id_or_url:
                    messagebox.showwarning("אזהרה",
                                           "לא נמצא קישור או מזהה קובץ תקני עבור הרשומה. מוחק רק את השורה מהגיליון.")

                    sheet_delete_result = self.backend.delete_row_from_sheet(sheet_name, row_index)
                    if sheet_delete_result is not True:
                        messagebox.showerror("שגיאת מחיקה", sheet_delete_result)
                    else:
                        messagebox.showinfo("מחיקה", "המחיקה הושלמה בהצלחה.")
                    return

                # Check if the URL is a Drive link
                if 'drive.google.com' in file_id_or_url:
                    # It's a Drive file, get the file ID from the URL and delete from Drive
                    file_id = file_id_or_url.split('/d/')[-1].split('/')[0]
                    drive_delete_result = self.backend.delete_file_from_drive(file_id)
                    if drive_delete_result is True:
                        sheet_delete_result = self.backend.delete_row_from_sheet(sheet_name, row_index)
                        if sheet_delete_result is not True:
                            messagebox.showerror("שגיאת מחיקה", sheet_delete_result)
                        else:
                            messagebox.showinfo("מחיקה", "המחיקה הושלמה בהצלחה.")
                    else:
                        messagebox.showerror("שגיאת מחיקה", drive_delete_result)
                else:
                    # It's not a Drive file (e.g., YouTube link), only delete the row from the sheet
                    sheet_delete_result = self.backend.delete_row_from_sheet(sheet_name, row_index)
                    if sheet_delete_result is not True:
                        messagebox.showerror("שגיאת מחיקה", sheet_delete_result)
                    else:
                        messagebox.showinfo("מחיקה", "המחיקה הושלמה בהצלחה.")
            else:
                messagebox.showwarning("אזהרה", "לא נמצאה רשומה מתאימה למחיקה בגיליון.")

        except Exception as e:
            messagebox.showerror("שגיאה", f"אירעה שגיאה: {e}")
        finally:
            self._reset_delete_form()

    def _reset_delete_form(self) -> None:
        """Resets the delete form to its initial state."""
        self.delete_content_type_var.set('file')
        self.delete_name_var.set('')


if __name__ == "__main__":
    root = tk.Tk()
    app = UploaderApp(root)
    root.mainloop()