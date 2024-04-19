import os.path
import pickle
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
# МББЭ 1305APD5kjZsE87yNSbORMDuDWF3QFjtDBqswHYD1dc0
# КНТ 1bNCPfD6I_81VrTs6Jgm922pg1ASvKtQnK4igOOsulfM
SAMPLE_SPREADSHEET_ID = "1305APD5kjZsE87yNSbORMDuDWF3QFjtDBqswHYD1dc0"
SAMPLE_RANGE_NAME = "B18:AD69"  # придется парсить название листа


def main():
    """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

    except HttpError as err:
        print(err)
    return values


def table_parsing() -> list:
    """
    Функция для получения массива из множества вложенных словарей

    :return: список, который имеет формат {"номер группы": {день недели: {"lessons":[]}}}
    """
    values = main()
    pattern = r'^[12].*\d$'
    students_groups = []
    flag_of_group_arr = False
    for elem in values:
        if flag_of_group_arr:
            break
        for i in range(len(elem)):
            if re.fullmatch(pattern, elem[i]):
                students_groups.append(elem[i])
                flag_of_group_arr = True
    print(students_groups)
    schedule_res = []
    for i in range(len(students_groups)):
        schedule_res.append({students_groups[i]: dict()})
    print("----------------------------------")
    print(schedule_res)
    print("----------------------------------")

    week_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
    for i in range(len(students_groups)):
        schedule_res[i][students_groups[i]] = {"понедельник": {"lessons": []}, "вторник": {"lessons": []},
                                               "среда": {"lessons": []},
                                               "четверг": {"lessons": []}, "пятница": {"lessons": []},
                                               "суббота": {"lessons": []}, "воскресенье": {"lessons": []}}

    print(schedule_res)
    print(values)

    pattern_for_classroom = r'\d{3}'
    pattern_for_time = r"\d{2}:\d{2}-\d{2}:\d{2}"
    number_of_cur_group = 0

    empty_string_counter = 0
    cur_week_day = ""
    cur_lesson_dict = {"name": "", "time": "", "auditorium": ""}
    pattern_of_auditorium = r"\d{3}|\d{3}(\s*\d*)*"
    print("-------------------------------------")
    #print(schedule_res[0]["22БИ1"]["понедельник"]["lessons"].append(cur_lesson_dict))
    print(schedule_res)
    print("-------------------------------------")
    for elem in values:
        cur_lesson_time = ""
        number_of_cur_group = 0
        for i in range(0, len(elem)):

            if empty_string_counter == 3:
                number_of_cur_group += 1
                empty_string_counter = 0
            if elem[i] in week_days:
                cur_week_day = elem[i]

                #append cur lesson dict
            if re.fullmatch(pattern_for_time, elem[i]):
                cur_lesson_time = elem[i]

            cur_group = students_groups[number_of_cur_group]
            if elem[i] == "":
                empty_string_counter += 1
            elif elem[i] != "":  #потенциальные проблемы
                empty_string_counter = 0
                cur_lesson_dict["time"] = cur_lesson_time
                if not re.fullmatch(pattern_of_auditorium, elem[i]):

                    cur_lesson_dict["name"] = elem[i]

                if re.fullmatch(pattern_of_auditorium, elem[i]):
                    cur_lesson_dict["auditorium"] = elem[i]

                    schedule_res[number_of_cur_group][cur_group][cur_week_day]["lessons"].append(cur_lesson_dict)
                    number_of_cur_group += 1
                    cur_lesson_dict = {"name": "", "time": "", "auditorium": ""}
    return schedule_res
