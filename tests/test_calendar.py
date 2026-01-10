import datetime
import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget, QListWidgetItem, QApplication

import narrion.tabs.calendar
from narrion.tabs.calendar import CalendarWidget, AddEventDialog, build

@pytest.fixture(scope="session")
def q_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
def test_calendar_widget_initialization(q_app, mocker):
    mock_events = [
        {"start": {"date": "2026-01-10"}, "summary": "Test Event"},
        {"start": {"date": "2026-01-15"}, "summary": "Another Event"},
    ]
    mock_update = mocker.Mock()
    mock_fetch = mocker.Mock(return_value=mock_events)

    cal = CalendarWidget(mock_events, mock_update, mock_fetch)
    assert cal._highlighted
    assert isinstance(cal, CalendarWidget)

def test_calendar_widget_on_date_clicked(q_app, mocker):
    events = [{"start": {"date": "2026-01-10"}, "summary": "Test Event"}]
    updated = []

    def update_callback(ev_list):
        updated.extend(ev_list)

    cal = CalendarWidget(events, update_callback, lambda y, m: [])
    cal.on_date_clicked(QDate(2026, 1, 10))

    assert len(updated) == 1
    assert updated[0]["summary"] == "Test Event"

def test_add_event_dialog_returns_data(q_app):
    dlg = AddEventDialog()
    dlg.title_edit.setText("My Event")
    dlg.date_edit.setDate(QDate(2026, 1, 20))

    title, date = dlg.get_data()
    assert title == "My Event"
    assert date == datetime.date(2026, 1, 20)

def test_build_returns_widget(q_app, mocker):
    mocker.patch("narrion.tabs.calendar.get_google_events", return_value=[])
    w = build()
    assert isinstance(w, QWidget)

def test_calendar_widget_marks_event_days(q_app, mocker):
    events = [{"start": {"date": "2026-02-05"}, "summary": "Test"}]
    cal = CalendarWidget(events, lambda x: None, lambda y, m: [])
    highlighted_dates = [d.toString("yyyy-MM-dd") for d in cal._highlighted]
    assert "2026-02-05" in highlighted_dates
