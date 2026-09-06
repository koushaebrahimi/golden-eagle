# -*- coding: utf-8 -*-
"""
Language translations for Golden Eagle.
"""

TRANSLATIONS = {
    'persian': {
        "Golden Eagle": "عقاب زرین",
        "Daily Work Time Recording System": "سیستم ثبت ساعات کاری روزانه",
        "Day Information": "اطلاعات روز",
        "Date (Day/Month/Year):": "تاریخ (روز/ماه/سال):",
        "Weekday:": "روز هفته:",
        "Day Type:": "نوع روز:",
        "In Time:": "ساعت ورود:",
        "Out Time:": "ساعت خروج:",
        "Load Day": "بارگذاری روز",
        "Save Day": "ذخیره روز",
        "Delete Day": "حذف روز",
        "Tasks and Subtasks": "تسک‌ها و زیرتسک‌ها",
        "Row": "ردیف",
        "Name": "نام",
        "Hours (HH:MM)": "ساعت (HH:MM)",
        "Description": "توضیحات",
        "Add Task": "افزودن تسک",
        "Add Subtask": "افزودن زیرتسک",
        "Delete Row": "حذف ردیف",
        "Edit Row": "ویرایش ردیف",
        "Auto-calc Task Hours": "محاسبه خودکار ساعت تسک",
        "Monthly Report": "گزارش ماهانه",
        "Check Consistency": "بررسی همخوانی",
        "View All Days": "مشاهده همه روزها",
        "Exit": "خروج",
        "Status: Ready": "وضعیت: آماده",
        "Error": "خطا",
        "Invalid date.": "تاریخ نامعتبر است.",
        "Not Found": "یافت نشد",
        "Success": "موفق",
        "Day saved successfully.": "روز با موفقیت ذخیره شد.",
        "Delete": "حذف",
        "Add": "افزودن",
        "Save": "ذخیره",
        "Cancel": "لغو",
        "Yes": "بله",
        "No": "خیر",
        "Confirm": "تأیید",
        "Leave": "مرخصی",
        "Information": "اطلاعات",
        "No days recorded.": "هیچ روزی ثبت نشده است.",
        "View All Days": "مشاهده همه روزها",
        "Date": "تاریخ",
        "Day Type": "نوع روز",
        "In Time": "ساعت ورود",
        "Out Time": "ساعت خروج",
        "Total Hours": "کارکرد",
        "Shortfall": "کسری",
        "Overwork": "اضافه کار",
        "Task Count": "تعداد تسک‌ها",
        "Close": "بستن",
        "Report": "گزارش",
        "Consistency Check": "بررسی همخوانی",
        "Done": "انجام شد",
        "OK": "تأیید",
        "Select Language": "انتخاب زبان",
        "English": "انگلیسی",
        "Persian": "فارسی",
    },
    'english': {
        "Golden Eagle": "Golden Eagle",
        "Daily Work Time Recording System": "Daily Work Time Recording System",
        "Day Information": "Day Information",
        "Date (Day/Month/Year):": "Date (Day/Month/Year):",
        "Weekday:": "Weekday:",
        "Day Type:": "Day Type:",
        "In Time:": "In Time:",
        "Out Time:": "Out Time:",
        "Load Day": "Load Day",
        "Save Day": "Save Day",
        "Delete Day": "Delete Day",
        "Tasks and Subtasks": "Tasks and Subtasks",
        "Row": "Row",
        "Name": "Name",
        "Hours (HH:MM)": "Hours (HH:MM)",
        "Description": "Description",
        "Add Task": "Add Task",
        "Add Subtask": "Add Subtask",
        "Delete Row": "Delete Row",
        "Edit Row": "Edit Row",
        "Auto-calc Task Hours": "Auto-calc Task Hours",
        "Monthly Report": "Monthly Report",
        "Check Consistency": "Check Consistency",
        "View All Days": "View All Days",
        "Exit": "Exit",
        "Status: Ready": "Status: Ready",
        "Error": "Error",
        "Invalid date.": "Invalid date.",
        "Not Found": "Not Found",
        "Success": "Success",
        "Day saved successfully.": "Day saved successfully.",
        "Delete": "Delete",
        "Add": "Add",
        "Save": "Save",
        "Cancel": "Cancel",
        "Yes": "Yes",
        "No": "No",
        "Confirm": "Confirm",
        "Leave": "Leave",
        "Information": "Information",
        "No days recorded.": "No days recorded.",
        "View All Days": "View All Days",
        "Date": "Date",
        "Day Type": "Day Type",
        "In Time": "In Time",
        "Out Time": "Out Time",
        "Total Hours": "Total Hours",
        "Shortfall": "Shortfall",
        "Overwork": "Overwork",
        "Task Count": "Task Count",
        "Close": "Close",
        "Report": "Report",
        "Consistency Check": "Consistency Check",
        "Done": "Done",
        "OK": "OK",
        "Select Language": "Select Language",
        "English": "English",
        "Persian": "Persian",
    }
}

_current_lang = 'persian'

def set_language(lang):
    global _current_lang
    _current_lang = lang

def get_language():
    return _current_lang

def _(text):
    return TRANSLATIONS.get(_current_lang, TRANSLATIONS['persian']).get(text, text)

def get_weekdays():
    if _current_lang == 'persian':
        return ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    return ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]

def get_day_types():
    if _current_lang == 'persian':
        return ["عادی", "مرخصی", "تعطیل رسمی", "اضافه کار", "دورکاری"]
    return ["Normal", "Leave", "Holiday", "Overtime", "Remote"]

def get_suggested_tasks():
    if _current_lang == 'persian':
        return ["مناقصات", "پروژه‌ها", "شرکت‌ها", "سایر"]
    return ["Tenders", "Projects", "Companies", "Other"]