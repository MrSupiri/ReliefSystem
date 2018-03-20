from tkinter import *
from tkinter import ttk
from stroage import DB, LOG
from collections import Counter
import random
import time
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.models import load_model
# from keras.optimizers import Adam
import os
# import numpy as np
import datetime
from urllib.request import Request
from urllib.request import urlopen
import json


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def exit_app():
    quit()


def maxvalue(dic):
    max_value = max(dic.values())  # maximum value
    max_keys = [k for k, v in dic.items() if v == max_value]
    return random.choice(max_keys)


def remove_none(dic):
    if None in dic.keys():
        del dic[None]
    return dic


# noinspection SqlResolve
def process_data(teacher_id):
    try:
        data = DB.get('SELECT * FROM Teachers WHERE Teacher_ID= (?)', teacher_id)[0][3:]

        class_ = remove_none(Counter(data[::2]))
        subject = remove_none(Counter(data[1::2]))

        grade = {}
        for cls in class_:
            if cls[:-2].strip('-') in class_.keys():
                grade[cls[:-2].strip('-')] += class_[cls]
            else:
                grade[cls[:-2].strip('-')] = class_[cls]
        section = {'1-5': 0, '6-8': 0, '9-11': 0, '12-13': 0}

        for key in grade:
            if 8 >= int(key) >= 6:
                section['6-8'] += grade[key]
            elif 11 >= int(key) >= 9:
                section['9-11'] += grade[key]
            elif 13 >= int(key) >= 11:
                section['12-13'] += grade[key]
            elif 5 >= int(key) >= 1:
                section['1-5'] += grade[key]

        classes = list(filter(None, data[1::2]))
        classes = ", ".join(str(x) for x in classes)

        if len(section.keys()) == 0 or len(grade.keys()) == 0 or len(subject.keys()) == 0 or len(classes) == 0:
            LOG.log.error('Empty TimeTable Detected => {}'.format((teacher_id, section, grade, subject, classes)))
            popupmsg('Empty TimeTable Detected\n'
                     'Teacher Will only appear all teachers list in Assign Relief Window', 'Error')

        if not DB.get('SELECT Teacher_ID FROM Metadata WHERE Teacher_ID = (?)', teacher_id):
            DB.put('INSERT INTO Metadata(Teacher_ID,Section,Grade,Subject,Classes) VALUES (?, ?, ?, ?, ?)',
                   teacher_id, maxvalue(section), int(maxvalue(grade)), maxvalue(subject), classes)
        else:
            DB.put('UPDATE Metadata SET Section = ?, Grade = ?, Subject = ?, Classes = ? WHERE Teacher_ID = ?',
                   maxvalue(section), int(maxvalue(grade)), maxvalue(subject), classes, teacher_id)

    except Exception as e:
        LOG.log.exception(e)
        popupmsg(e)


def popupmsg(msg, title=''):
    popup = Tk()
    popup.wm_title(title)
    label = ttk.Label(popup, text=msg, font=SMALL_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def clearTimeTable(dic):
    for d in dic:
        dic[d].delete(0, END)
        dic[d].insert(0, '')


def get_teachers_tech_to_class(cls):
    teachers = []
    data = DB.get('SELECT Teacher_ID,Classes FROM Metadata')
    for d in data:
        if cls in d[1]:
            teachers.append(d[0])
    return teachers


def sendSMS(sms_dic, frame):
    res = {'message': 'Hello', 'destinationAddresses': ['tel:94771122336'], 'password': 'password',
           'applicationId': 'APP_000001'}

    for sms in sms_dic:
        res['message'] = sms_dic[sms]
        # res['destinationAddresses'] = ['tel:94{}'.format(sms)]
        r = urlopen(Request("http://localhost:7000/sms/send", json.dumps(res).encode('utf8'),
                            headers={"Content-Type": "application/json", "Accept": "application/json"}))
        if r.getcode() != 200:
            popupmsg('Message was not Sent to {}'.format(sms), 'SMS Failed')
        else:
            del sms_dic[sms]

    frame.destroy()


def get_unique(a, b):
    return list(set(a).difference(b))


def AddTeacherTODB(dic, quick=False):
    dataDic = {}

    for d in dic:
        if dic[d].get() == '' or dic[d].get() == ' ':
            dataDic[d] = None
        else:
            if dic[d].get().isdigit():
                dataDic[d] = int(dic[d].get())
            else:
                dataDic[d] = dic[d].get()
    time.sleep(0.5)
    if dataDic['Teacher_Name'] is None or type(dataDic['Teacher_Name']) != str:
        popupmsg('Please Enter a Valid Name')
        return
    elif dataDic['Teacher_ID'] is None or type(dataDic['Teacher_ID']) != int:
        popupmsg('Please Enter a Valid Teacher ID')
        return
    elif dataDic['Telephone_Number'] is None or type(dataDic['Telephone_Number']) != int \
            or len(str(dataDic['Telephone_Number'])) != 9:
        popupmsg('Please Enter a Valid Telephone Number')
        return

    if DB.get("SELECT Teacher_ID FROM Teachers WHERE Teacher_ID = ?", dataDic['Teacher_ID']):
        popupmsg("Teacher ID {} is Already in the Database If You wish to delete or change TimeTable for that ID "
                 "please Use Modify/Delete Option".format(dataDic['Teacher_ID']), title='Duplicate ID')
        return

    teacherID = dataDic.pop('Teacher_ID')

    DB.put('''INSERT INTO Teachers(Teacher_ID) VALUES (?)''', teacherID)

    for d in dataDic:
        # noinspection SqlResolve
        DB.put('UPDATE Teachers SET `' + str(d) + '` = (?) WHERE Teacher_ID = (?)', dataDic[d], teacherID)

    process_data(teacherID)

    if not quick:
        clearTimeTable(dic)


def findTeacher(dic):
    TID = dic['Teacher_ID'].get()
    TP = dic['Telephone_Number'].get()
    TNAME = dic['Teacher_Name'].get()
    clearTimeTable(dic)
    if not TID == '' or TID == ' ':
        for d in dic:
            data = DB.get('SELECT "' + str(d) + '" FROM Teachers WHERE Teacher_ID = (?)', int(TID), readOne=True)
            if data is None:
                popupmsg("Can't Find Teacher with the Teacher ID {}".format(TID), title='No Match Found')
                return
            if data[0] is not None:
                dic[d].insert(0, data[0])
        return
    if not TP == '' or TP == ' ':
        for d in dic:
            data = DB.get('SELECT "' + str(d) + '" FROM Teachers WHERE Telephone_Number = (?)', int(TP), readOne=True)
            if data is None:
                popupmsg("Can't Find Teacher with the Telephone Number {}".format(TP), title='No Match Found')
                return
            if data[0] is not None:
                dic[d].insert(0, data[0])
        return
    if not TNAME == '' or TNAME == ' ':
        for d in dic:
            data = DB.get('SELECT "' + str(d) + '" FROM Teachers WHERE Teacher_Name = (?)', str(TNAME), readOne=True)
            if data is None:
                popupmsg("Can't Find Teacher with the Name {}".format(TNAME), title='No Match Found')
                return
            if data[0] is not None:
                dic[d].insert(0, data[0])
        return


def dropTeacher(dic, quick=False):
    TID = dic['Teacher_ID'].get()
    TP = dic['Telephone_Number'].get()
    TNAME = dic['Teacher_Name'].get()

    if not TID == '' or TID == ' ':
        DB.put('DELETE FROM Teachers WHERE Teacher_ID = (?)', int(TID))
        if not quick:
            clearTimeTable(dic)
        return
    if not TP == '' or TP == ' ':
        DB.put('DELETE FROM Teachers WHERE Telephone_Number = (?)', int(TP))
        if not quick:
            clearTimeTable(dic)
        return
    if not TNAME == '' or TNAME == ' ':
        DB.put('DELETE FROM Teachers WHERE Teacher_Name = (?)', str(TNAME))
        if not quick:
            clearTimeTable(dic)
        return


def updateTeacher(dic, quick=False):
    dataDic = {}

    for d in dic:
        if dic[d].get() == '' or dic[d].get() == ' ':
            dataDic[d] = None
        else:
            if dic[d].get().isdigit():
                dataDic[d] = int(dic[d].get())
            else:
                dataDic[d] = dic[d].get()

    if dataDic['Teacher_Name'] is None or type(dataDic['Teacher_Name']) != str:
        popupmsg('Please Enter a Valid Name')
        return
    elif dataDic['Teacher_ID'] is None or type(dataDic['Teacher_ID']) != int:
        popupmsg('Please Enter a Valid Teacher ID')
        return
    elif dataDic['Telephone_Number'] is None or type(dataDic['Telephone_Number']) != int \
            or len(str(dataDic['Telephone_Number'])) != 9:
        popupmsg('Please Enter a Valid Telephone Number')
        return

    teacherID = dataDic.pop('Teacher_ID')

    for d in dataDic:
        # noinspection SqlResolve
        DB.put('UPDATE Teachers SET `' + str(d) + '` = (?) WHERE Teacher_ID = (?)', dataDic[d], teacherID)

    if not quick:
        clearTimeTable(dic)

    process_data(teacherID)


# class DQNAgent:
#     def __init__(self, MODEL_NAME='relief'):
#         self.model_loaded = False
#         self.MODEL_NAME = MODEL_NAME + '.h5'
#         self.learning_rate = 0.001
#         if os.path.isfile('data/' + self.MODEL_NAME):
#             self.model = load_model('data/' + self.MODEL_NAME)
#             self.model_loaded = True
#         else:
#             self.model = self._build_model()
#
#     @staticmethod
#     def _build_model():
#         model = Sequential()
#         model.add(Dense(16, activation='relu', input_shape=(5,)))
#         model.add(Dense(8, activation='relu'))
#         model.add(Dense(2, activation='softmax'))
#         model.compile(loss='categorical_crossentropy',
#                       optimizer=Adam(lr=1e-4))
#         return model
#
#     def predict(self, INPUT):
#         act_values = self.model.predict(INPUT)
#         return act_values
#
#     def save(self):
#         self.model.save('data/' + self.MODEL_NAME)
#
#     def fit(self, cls, tid):
#         try:
#             classes = DB.get('SELECT classes FROM Metadata WHERE Teacher_ID = ?', tid)[0][0]
#         except IndexError:
#             classes = ''
#
#         if cls in classes:
#             teach_to_class = 1
#         else:
#             teach_to_class = 0
#
#         free_today = 0
#         free_total = 0
#         working_today = 0
#         working_total = 0
#         for day in range(1, 6):
#             for period in range(1, 9):
#                 # noinspection SqlResolve
#                 if DB.get('SELECT `D{0}P{1}-S`,`D{0}P{1}-C` FROM Teachers WHERE Teacher_ID = ?'.format(day, period),
#                           tid)[0] == (None, None):
#                     free_today += 1
#                     if day == current_day_of_week:
#                         free_total += 1
#                 else:
#                     working_today += 1
#                     if day == current_day_of_week:
#                         working_total += 1
#         X_ = np.array([teach_to_class, free_today, free_total, working_today, working_total]).reshape([-1, 5])
#         Y_ = np.array([0, 1]).reshape([-1, 2])
#         LOG.log.info('Fitting Data => {} => {}'.format(X_, Y_))
#         self.model.fit(X_, Y_, epochs=1, verbose=0)
#         self.save()
#
#
# def data_process(data_set):
#     if not data_set:
#         return random.randint(0, 200)
#
#     INPUT = []
#     for data in data_set:
#         teach_2_cla, tid = data
#         free_today = 0
#         free_total = 0
#         working_today = 0
#         working_total = 0
#         for day in range(1, 6):
#             for period in range(1, 9):
#                 # noinspection SqlResolve
#                 if DB.get('SELECT `D{0}P{1}-S`,`D{0}P{1}-C` FROM Teachers WHERE Teacher_ID = ?'.format(day, period),
#                           tid)[0] == (None, None):
#                     free_today += 1
#                     if day == current_day_of_week:
#                         free_total += 1
#                 else:
#                     working_today += 1
#                     if day == current_day_of_week:
#                         working_total += 1
#         INPUT.append(np.array([teach_2_cla, free_today, free_total, working_today, working_total]).reshape([-1, 5]))
#     return data_set[np.array([i[0] for i in AI.predict(np.array(INPUT).reshape([len(INPUT), 5]))]).argmax()][1]
#
#
# def getPrediction(teachers_tech_to_class, teachers_tech_to_section):
#     teachers_tech_to_class = [[1, tid] for tid in teachers_tech_to_class]
#     teachers_tech_to_section = [[0, tid] for tid in teachers_tech_to_section]
#     prediction = data_process(teachers_tech_to_class + teachers_tech_to_section)
#
#     return '{} - {}'.format(prediction,
#                             DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = ?', prediction)[0][0])


def update_time_popup():
    popup = Tk()
    popup.wm_title('Critical Error')
    ttk.Label(popup, text='This software is made to only run on weekdays'
                          ' If not software will run into issues', font=SMALL2_FONT).pack()
    ttk.Label(popup, text='If Today is weekday pleses update Windows Time'
                          ' If not type any week date', font=SMALL2_FONT).pack()
    ttk.Label(popup, text='you wish at the box below in format YYYY/MM/DD', font=SMALL2_FONT).pack()
    ttk.Label(popup, text='', font=SMALL2_FONT).pack()
    v = StringVar()
    time_picker = ttk.Entry(popup, textvariable=v, justify=CENTER)
    v.set('2030/10/15')
    time_picker.pack(pady=5)
    B1 = ttk.Button(popup, text="Update Time", command=lambda: update_date(v.get(), popup))
    B1.pack(pady=10)
    popup.mainloop()


def update_date(date, popup):
    # noinspection PyBroadException
    try:
        global current_day, current_day_of_week
        current_day = datetime.datetime.strptime(date, '%Y/%m/%d')
        popup.destroy()
        current_day_of_week = current_day.weekday() + 1
        dates[0] = current_day
        dates[1] = current_day_of_week
    except Exception as e:
        popupmsg('Please Enter Time in YYYY/MM/DD format', 'Invalid Date')


LARGE_FONT = ("Verdana", 14)
FONT_Header = ("Verdana", 16)
NORM_FONT = ("Helvetica", 12)
SMALL2_FONT = ("Helvetica", 11)
SMALL_FONT = ("Helvetica", 10)
day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
SMS_DICT = {}
num = [None, '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th']
sendDict = {}
relief_dict = {}
# AI = DQNAgent()
dates = [None, None]
absent_list = []

if not 1 <= datetime.datetime.today().weekday() + 1 <= 5:
    update_time_popup()
    current_day, current_day_of_week = dates
else:
    current_day = datetime.datetime.today()
    current_day_of_week = current_day.weekday() + 1
