import datetime
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build as google_build
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_google_events(center_year, center_month):
    """Fetch events from Google Calendar for the month centered around"""
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("./data/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = google_build("calendar", "v3", credentials=creds)

    if center_month == 1:
        prev_month_start = datetime.date(center_year - 1, 12, 1)
    else:
        prev_month_start = datetime.date(center_year, center_month - 1, 1)

    if center_month == 12:
        next_month_start = datetime.date(center_year + 1, 1, 1)
    else:
        next_month_start = datetime.date(center_year, center_month + 1, 1)

    time_min = prev_month_start.isoformat() + "T00:00:00Z"
    after_next = (next_month_start.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    time_max = after_next.isoformat() + "T00:00:00Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
            maxResults=300,
        )
        .execute()
    )

    events = events_result.get("items", [])

    filtered = []
    for ev in events:
        title = ev.get("summary", "")
        if title.startswith("[GAME]"):
            ev["summary"] = title.replace("[GAME]", "").strip()
            filtered.append(ev)

    return filtered


def add_google_event(title, date):
    """Add an event to Google Calendar"""
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = google_build("calendar", "v3", credentials=creds)

    event = {
        "summary": f"[GAME] {title}",
        "start": {"date": date.isoformat()},
        "end": {"date": (date + datetime.timedelta(days=1)).isoformat()},
    }

    service.events().insert(calendarId="primary", body=event).execute()


def delete_google_event(event_id):
    """Delete an event from Google Calendar by its ID"""
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = google_build("calendar", "v3", credentials=creds)
    service.events().delete(calendarId="primary", eventId=event_id).execute()


class CalendarWidget(QCalendarWidget):
    """Widget for displaying a calendar with highlighted event days."""

    def __init__(self, events, update_callback, fetch_callback):
        super().__init__()
        self.events = events
        self.update_callback = update_callback
        self.fetch_callback = fetch_callback
        self.setGridVisible(True)

        self.highlight = QTextCharFormat()
        self.highlight.setBackground(QColor("#024b08"))

        self._highlighted = []

        self.mark_event_days()
        self.clicked.connect(self.on_date_clicked)

        self.currentPageChanged.connect(self.on_month_changed)

    def clear_highlights(self):
        """Clear all highlighted days in the calendar."""
        fmt = QTextCharFormat()
        for d in self._highlighted:
            self.setDateTextFormat(d, fmt)
        self._highlighted.clear()

    def mark_event_days(self):
        """Highlight days in the calendar that have events."""
        self.clear_highlights()
        for event in self.events:
            start = event.get("start", {})
            date_str = start.get("date") or start.get("dateTime")
            if not date_str:
                continue

            date = QDate.fromString(date_str[:10], "yyyy-MM-dd")

            if date.isValid():
                self.setDateTextFormat(date, self.highlight)
                self._highlighted.append(date)

    def on_month_changed(self, year, month):
        """Fetch events for the newly displayed month and update highlights."""
        self.events = self.fetch_callback(year, month)
        self.mark_event_days()

    def on_date_clicked(self, date):
        """Update the event list based on the selected date."""
        selected = []

        for event in self.events:
            start = event.get("start", {})
            date_str = start.get("date") or start.get("dateTime")

            if date_str and date_str.startswith(date.toString("yyyy-MM-dd")):
                selected.append(event)

        self.update_callback(selected)


class AddEventDialog(QDialog):
    """Dialog for adding a new event."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj wydarzenie")

        layout = QFormLayout(self)

        self.title_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        layout.addRow("Tytuł:", self.title_edit)
        layout.addRow("Data:", self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_data(self):
        """Retrieve the entered event title and date."""
        return (
            self.title_edit.text().strip(),
            self.date_edit.date().toPython(),
        )


def build() -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(6, 6, 6, 6)

    title = QLabel("Terminarz sesji")
    title.setAlignment(Qt.AlignCenter)
    title.setMaximumHeight(40)

    v.addWidget(title)

    today = datetime.date.today()
    events = get_google_events(today.year, today.month)

    event_list = QListWidget()

    def update_event_details(ev_list):
        """Update the event list widget with events for the selected day."""
        event_list.clear()

        if not ev_list:
            item = QListWidgetItem("Brak wydarzeń tego dnia")
            item.setFlags(Qt.NoItemFlags)
            event_list.addItem(item)
            return

        for ev in ev_list:
            start = ev["start"].get("dateTime", ev["start"].get("date"))
            text = f"{start} — {ev.get('summary', 'Bez nazwy')}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, ev)
            event_list.addItem(item)

    def fetch_for_month(year, month):
        """Fetch events for the specified month."""
        return get_google_events(year, month)

    cal = CalendarWidget(events, update_event_details, fetch_for_month)

    cal.setMinimumHeight(280)

    right = QVBoxLayout()
    right.addWidget(QLabel("Szczegóły wydarzeń"))
    right.addWidget(event_list)
    add_event_btn = QPushButton("Dodaj wydarzenie")
    right.addWidget(add_event_btn)

    def on_add_event():
        """Handle adding a new event."""
        dlg = AddEventDialog(w)
        if dlg.exec() != QDialog.Accepted:
            return

        title, date = dlg.get_data()
        if not title:
            return

        add_google_event(title, date)

        cal.events = get_google_events(date.year, date.month)
        cal.mark_event_days()

        current_date = cal.selectedDate()
        daily = [
            e
            for e in cal.events
            if (
                e.get("start", {}).get("date") or e.get("start", {}).get("dateTime", "")
            ).startswith(current_date.toString("yyyy-MM-dd"))
        ]
        update_event_details(daily)

    add_event_btn.clicked.connect(on_add_event)
    delete_event_btn = QPushButton("Usuń wydarzenie")
    right.addWidget(delete_event_btn)

    def on_delete_event():
        """Handle deleting the selected event."""
        item = event_list.currentItem()
        if not item:
            return

        ev = item.data(Qt.UserRole)
        if not ev:
            return

        event_id = ev.get("id")
        if not event_id:
            return

        delete_google_event(event_id)

        start = ev["start"].get("dateTime", ev["start"].get("date"))
        date = QDate.fromString(start[:10], "yyyy-MM-dd")

        cal.events = get_google_events(date.year(), date.month())
        cal.mark_event_days()

        current_date = cal.selectedDate()
        remaining = [
            e
            for e in cal.events
            if (
                e.get("start", {}).get("date") or e.get("start", {}).get("dateTime", "")
            ).startswith(current_date.toString("yyyy-MM-dd"))
        ]
        update_event_details(remaining)

    delete_event_btn.clicked.connect(on_delete_event)

    split = QSplitter(Qt.Horizontal)
    left_frame = QWidget()
    lf_layout = QVBoxLayout(left_frame)
    lf_layout.addWidget(cal)
    split.addWidget(left_frame)

    right_frame = QWidget()
    rf_layout = QVBoxLayout(right_frame)
    rf_layout.addLayout(right)
    split.addWidget(right_frame)
    split.setStretchFactor(0, 2)
    split.setStretchFactor(1, 1)

    v.addWidget(split)
    return w
