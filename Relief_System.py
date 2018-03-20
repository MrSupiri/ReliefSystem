from helper_code import *


# Main Class
class Application(Tk):
    def __init__(self, *args, **kwargs):
        try:
            Tk.__init__(self, *args, **kwargs)

            Tk.iconbitmap(self, default="data/favicon.ico")
            Tk.wm_title(self, "Relief Period Finder")

            container = Frame(self)
            container.pack(side="top", fill="both", expand=True)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            menubar = Menu(container)
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="Send SMSs", command=lambda: self.showSMSDict())
            filemenu.add_command(label="Save settings", command=lambda: popupmsg('Not supported just yet!'))
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=exit_app)
            menubar.add_cascade(label="File", menu=filemenu)

            modify = Menu(menubar, tearoff=0)
            modify.add_command(label="Add New Teacher", command=lambda: Add_Teacher())
            modify.add_separator()
            modify.add_command(label="Modify TimeTable", command=lambda: Modify_Teacher())
            modify.add_command(label="Remove Teacher", command=lambda: Modify_Teacher())
            menubar.add_cascade(label="Modify", menu=modify)

            Tk.config(self, menu=menubar)

            self.frames = {}

            frame = HomePage(container)

            self.frames[HomePage] = frame

            frame.grid(row=0, column=0, sticky="nsew")

            frame.tkraise()
        except Exception as e:
            LOG.log.exception(e)

    @staticmethod
    def showSMSDict():
        popup = Tk()
        popup.wm_title('Send SMSs')
        for sms in SMS_DICT:
            row = Frame(popup)
            text = "{} - {} => ".format(SMS_DICT[sms][0], sms)
            ttk.Label(row, text=text, font=SMALL_FONT).pack(side=LEFT, expand=True, fill=BOTH)
            text = ""
            for period in sorted(SMS_DICT[sms][1]):
                text += "{} Period - {}\n".format(num[int(period[0])], period[1])
            ttk.Label(row, text=text[:-1], font=SMALL_FONT).pack(side=RIGHT, padx=10, expand=True, fill=BOTH)
            row.pack(side=TOP, pady=5)
            sendDict[sms] = "Reliefs to Cover, " + text.replace('\n', ', ')[:-2]
            if len(sendDict[sms]) > 160:
                popupmsg("SMS for {} is exceeded SMS character limit\nIf you Want to Remove a Period You have to "
                         "Restart the Softwate".format(sms), title='SMS character limit Exceeded')
        B1 = ttk.Button(popup, text="Send All SMSs Now", command=lambda: sendSMS(sendDict, popup))
        B1.pack(pady=5)
        popup.mainloop()


class HomePage(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.CurrentTID = None
        self.TimeTable = {}
        self.data = {}

        self.data = DB.get('SELECT Teacher_ID,Teacher_Name FROM Teachers ORDER BY Teacher_ID ASC')

        self.Lb1 = Listbox(self)
        self.Lb2 = Listbox(self)

        for d in self.data:
            self.Lb1.insert(d[0], '{:03} - {}'.format(d[0], d[1]))

        for d in DB.get('SELECT History.Teacher_ID, Teachers.Teacher_Name FROM History, Teachers WHERE '
                        'History.Teacher_ID = Teachers.Teacher_ID AND History.Date > ? AND History.Date < ?',
                        time.mktime(datetime.datetime.today().date().timetuple()),
                        time.mktime((datetime.date.today() + datetime.timedelta(days=1)).timetuple())):
            self.Lb2.insert(d[0], '{:03} - {}'.format(d[0], d[1]))

        self.Lb1.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)
        self.Lb2.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)

        classTimeTable = Frame(self)
        i = 0
        for day in day_list:
            ttk.Label(classTimeTable, text=day, font=NORM_FONT).grid(row=0, column=i, columnspan=3)
            i += 3
        self.title = ttk.Label(self, text='TimeTable for -------------', font=FONT_Header)
        self.title.pack(expand=True, anchor=CENTER)

        D = 1
        P = 1
        for k in range(2, 10):
            for i in range(0, 15, 3):
                self.TimeTable['D{}P{}-C'.format(D, P)] = ttk.Label(classTimeTable, text="-----------", font=SMALL_FONT)
                self.TimeTable['D{}P{}-C'.format(D, P)].grid(row=k, column=i, padx=3, pady=3)
                self.TimeTable['D{}P{}-S'.format(D, P)] = ttk.Label(classTimeTable, text="-----------", font=SMALL_FONT)
                self.TimeTable['D{}P{}-S'.format(D, P)].grid(row=k, column=i + 1, padx=3, pady=3)
                D += 1
            P += 1
            D = 1
        classTimeTable.pack(pady=10, padx=20, side=TOP, expand=True, fill=BOTH, anchor=CENTER)
        ttk.Label(self, text="Peroids Missed", font=LARGE_FONT).pack(pady=8)

        date_picker = Frame(self)
        ttk.Label(date_picker, text="Enter The Date in YYYY/MM/DD Format", font=SMALL_FONT).pack(side="top")
        ttk.Label(date_picker, text="Starting Date", font=SMALL_FONT).pack(side="left", pady=5, padx=5)
        self.time_start = ttk.Entry(date_picker)
        self.time_start.pack(side='left', padx=5)
        ttk.Label(date_picker, text="Ending Date", font=SMALL_FONT).pack(side="left", padx=5)
        self.time_end = ttk.Entry(date_picker)
        self.time_end.pack(side="left", padx=5)
        date_picker.pack()

        misses = Frame(self)
        ttk.Label(misses, text="Peroids Misssed In The TimeFrame", font=NORM_FONT).pack()
        self.relief = ttk.Label(misses, text="", font=SMALL_FONT)
        self.relief.pack()
        misses.pack(side=TOP, padx=40, expand=True)

        btns = Frame(self)
        self.assign_btn = ttk.Button(btns, text="Assign Relief", command=lambda: Assign_Relief(self.CurrentTID),
                                     state=DISABLED)
        self.assign_btn.pack(pady=10, padx=30, side=RIGHT)

        self.absent_btn = ttk.Button(btns, text="Mark Absent", command=lambda: self.MarkAbsent(), state=DISABLED)
        self.absent_btn.pack(pady=10, padx=30, side=RIGHT)
        self.present_btn = ttk.Button(btns, text="Mark Present", command=lambda: self.MarkPresent(), state=DISABLED)
        self.present_btn.pack(pady=10, padx=30, side=RIGHT)

        btns.pack()

        self.pool()

    def pool(self):
        current = None
        if self.Lb1.curselection() != ():
            current = self.Lb1.get(self.Lb1.curselection()[0])
            self.absent_btn.config(state=NORMAL)
            self.present_btn.config(state=DISABLED)
        elif self.Lb2.curselection() != ():
            current = self.Lb2.get(self.Lb2.curselection()[0])
            self.absent_btn.config(state=DISABLED)
            self.assign_btn.config(state=NORMAL)
            self.present_btn.config(state=NORMAL)
        else:
            self.absent_btn.config(state=DISABLED)
            self.present_btn.config(state=DISABLED)
            self.assign_btn.config(state=DISABLED)
        if current is not None:
            current = int(current.split('-')[0].strip())
            if current != self.CurrentTID:
                self.updateTable(current)
        if self.time_start.get() != '' and self.time_end.get() != '':
            # noinspection PyBroadException
            try:
                self.updateSummary(datetime.datetime.strptime(self.time_start.get(), '%Y/%m/%d').timestamp(),
                                   datetime.datetime.strptime(self.time_end.get(), '%Y/%m/%d').timestamp())
            except:
                self.relief.config(text='')
        else:
            self.relief.config(text='')

        self.after(250, self.pool)

    def updateTable(self, TID):
        self.CurrentTID = TID
        for d in self.TimeTable:
            data = DB.get('SELECT "' + str(d) + '" FROM Teachers WHERE Teacher_ID = (?)', TID, readOne=True)
            if data is None:
                popupmsg("Can't Find Teacher with the Teacher ID {}".format(TID), title='No Match Found')
                return
            if data[0] is not None:
                self.TimeTable[d].config(text=str(data[0]))
            else:
                self.TimeTable[d].config(text='------')
        self.title.config(
            text='TimeTable for {}'.format(DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = (?)',
                                                  TID, readOne=True)[0]))
        return

    def MarkAbsent(self):
        if self.CurrentTID is None:
            popupmsg('Please Select a Teacher First', title='Invalid Teacher')
        else:
            data = DB.get('SELECT Date FROM History WHERE Teacher_ID = ? ORDER BY Date DESC', self.CurrentTID,
                          readOne=True)
            epoch = int(time.time())
            if data is not None and datetime.datetime.fromtimestamp(data[0]).date() == current_day.date():
                popupmsg('This Teacher was Already Mark Absent', title='Duplicate Entry')
            else:
                DB.put("INSERT INTO History(Teacher_ID, Date) VALUES(?, ?)", self.CurrentTID, epoch)
            relief_dict[self.CurrentTID] = ['D{}P{}'.format(2, k)
                                            for k in range(1, 9)]

            self.Lb1.delete(ANCHOR)
            self.Lb2.insert(self.CurrentTID, '{:03} - {}'.format(self.data[self.CurrentTID][0],
                                                                 self.data[self.CurrentTID][1]))

    def MarkPresent(self):
        if self.CurrentTID is None:
            popupmsg('Please Select a Teacher First', title='Invalid Teacher')
        else:
            data = DB.get('SELECT ID,Date FROM History WHERE Teacher_ID = ? ORDER BY Date DESC', self.CurrentTID,
                          readOne=True)
            if data is not None and datetime.datetime.fromtimestamp(data[1]).date() == datetime.datetime.today().date():
                DB.put("DELETE FROM History WHERE ID = ?", data[0])
            else:
                popupmsg('Teacher was not Marked Absent Today', title='Invalid Selection')

            self.Lb2.delete(ANCHOR)
            self.Lb1.insert(self.CurrentTID, '{:03} - {}'.format(self.data[self.CurrentTID][0],
                                                                 self.data[self.CurrentTID][1]))

    def updateSummary(self, start, end):
        misses = DB.get('SELECT Date FROM History WHERE Teacher_ID = ? AND Date > ? AND Date < ?', self.CurrentTID,
                        start, end)
        thisWeek = {}
        for miss in misses:
            thisWeek = self.getMissPeriods(thisWeek, miss[0])

        txt = ''
        for d in thisWeek:
            txt += '{} - {}\n'.format(thisWeek[d], d)

        self.relief.config(text=txt[:-1])

    def getMissPeriods(self, periodsDict, d):
        d = int(datetime.datetime.fromtimestamp(d).weekday()) + 1
        for i in range(1, 8):
            # noinspection SqlResolve
            c = DB.get('SELECT `D{}P{}-C` FROM Teachers WHERE Teacher_ID = (?)'.format(d, i), self.CurrentTID)[0]
            # noinspection SqlResolve
            s = DB.get('SELECT `D{}P{}-S` FROM Teachers WHERE Teacher_ID = (?)'.format(d, i), self.CurrentTID)[0]
            k = '{} - {}'.format(c[0], s[0])
            if k in periodsDict:
                periodsDict[k] += 1
            else:
                periodsDict[k] = 1

        return periodsDict


class Assign_Relief(Frame):
    def __init__(self, teacher_id):
        self.relief_assign = Tk()
        Frame.__init__(self, self.relief_assign)
        self.relief_assign.geometry("1024x576")
        self.relief_assign.wm_title("Assign Relief")

        self.cls = 'dkjgklsdjfeopfj'
        self.inc = 0
        self.current_selection = None
        self.day = current_day_of_week
        # self.AI_Prefix = "AI's Prediction :- "
        self.selected_teacher = None
        self.period = 0
        self.section = DB.get('SELECT Section FROM Metadata WHERE Teacher_ID = ?', teacher_id)[0][0]
        self.teacher_name = DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = ?', teacher_id)[0][0]

        ttk.Label(self.relief_assign, text="Assign Relief for {}-{}'s Peroids".format(teacher_id, self.teacher_name),
                  font=FONT_Header).pack(side="top", pady=20)

        data = []
        for i in range(1, 9):
            # noinspection SqlResolve
            data.append(
                DB.get('SELECT `D{0}P{1}-C`, `D{0}P{1}-S` FROM Teachers WHERE Teacher_ID = (?)'.format(self.day, i),
                       teacher_id)[0])

        self.names = Frame(self.relief_assign)
        self.Lb1 = Listbox(self.names)
        i = 0
        for d in data:
            if d[0] is None or d[1] is None:
                self.Lb1.insert(i, 'Free Period'.format(d[0], d[1]))
            else:
                self.Lb1.insert(i, '{} - {}'.format(d[0], d[1]))
            i += 1
        self.Lb1.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)

        self.Lb2 = Listbox(self.names)
        self.Lb2.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)

        self.Lb3 = Listbox(self.names)
        self.Lb3.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)

        self.Lb4 = Listbox(self.names)
        self.Lb4.pack(side=LEFT, fill=BOTH, pady=5, padx=5, expand=True)
        self.names.pack(side=TOP, fill=BOTH, pady=5, padx=5, expand=True)

        # self.prediction = ttk.Label(self.relief_assign, text=self.AI_Prefix, font=NORM_FONT)
        # self.prediction.pack(side=LEFT, pady=10, padx=5)
        # self.Lb5 = Listbox(self.relief_assign, height=1)
        # self.Lb5.pack(side=LEFT, pady=5, padx=5)

        ttk.Button(self.relief_assign, text="Assign", command=lambda: self.assign()).pack(pady=10, padx=30, side=RIGHT)

        self.pool()
        self.relief_assign.mainloop()

    def pool(self):
        if self.Lb1.curselection() != ():
            current = self.Lb1.get(self.Lb1.curselection()[0])
            self.period = int(self.Lb1.index(ACTIVE)) + 1
            if current == 'Free Period':
                self.inc = 0
                self.Lb2.delete(0, END)
                self.Lb3.delete(0, END)
                self.Lb4.delete(0, END)
                # self.Lb5.delete(0, END)
                self.current_selection = None
            elif current != self.current_selection:
                self.current_selection = current
                self.cls = current.split('-')[0].strip() + '-' + current.split('-')[1].strip()
                self.inc = 0
                self.Lb2.delete(0, END)
                self.Lb3.delete(0, END)
                self.Lb4.delete(0, END)
                # self.Lb5.delete(0, END)
                teachers_tech_to_class = self.get_teachers_tech_to_class()
                self.Lb2.delete(0, END)
                for tid in teachers_tech_to_class:
                    name = DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = ?', tid)[0][0]
                    self.Lb2.insert(self.inc, '{} - {}'.format(tid, name))
                    self.inc += 1
                teachers_tech_to_section = get_unique(self.get_teachers_tech_to_section(), teachers_tech_to_class)
                self.Lb3.delete(0, END)
                for tid in teachers_tech_to_section:
                    name = DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = ?', tid)[0][0]
                    self.Lb3.insert(self.inc, '{} - {}'.format(tid, name))
                    self.inc += 1

                all_free_teachers = get_unique(self.get_all_free_teachers(), teachers_tech_to_section)
                self.Lb4.delete(0, END)
                for tid in all_free_teachers:
                    name = DB.get('SELECT Teacher_Name FROM Teachers WHERE Teacher_ID = ?', tid)[0][0]
                    self.Lb4.insert(self.inc, '{} - {}'.format(tid, name))
                    self.inc += 1
                # self.Lb5.delete(0, END)
                # self.Lb5.insert(self.inc, getPrediction(teachers_tech_to_class, teachers_tech_to_section))
                self.inc += 1

        if self.Lb2.curselection() != ():
            self.selected_teacher = int(self.Lb2.get(self.Lb2.curselection()[0]).split('-')[0].strip())
        elif self.Lb3.curselection() != ():
            self.selected_teacher = int(self.Lb3.get(self.Lb3.curselection()[0]).split('-')[0].strip())
        elif self.Lb4.curselection() != ():
            self.selected_teacher = int(self.Lb4.get(self.Lb4.curselection()[0]).split('-')[0].strip())
        # elif self.Lb5.curselection() != ():
        #     self.selected_teacher = int(self.Lb5.get(self.Lb5.curselection()[0]).split('-')[0].strip())

        self.after(250, self.pool)

    def get_teachers_tech_to_class(self):
        teachers = []
        data = DB.get('SELECT Teacher_ID,Classes FROM Metadata')
        for d in data:
            if self.cls in d[1]:
                if self.is_free(d[0]):
                    teachers.append(d[0])
        return teachers

    def get_teachers_tech_to_section(self):
        teachers = []
        data = DB.get('SELECT Teacher_ID,Section FROM Metadata')
        for d in data:
            if self.section == d[1]:
                if self.is_free(d[0]):
                    teachers.append(d[0])
        return teachers

    def get_all_free_teachers(self):
        teachers = []
        data = DB.get('SELECT Teacher_ID FROM Teachers')
        for d in data:
            if self.is_free(d[0]):
                teachers.append(d[0])
        return teachers

    def assign(self):
        data = DB.get('SELECT Teacher_Name,Telephone_Number FROM Teachers WHERE Teacher_ID = ?',
                      self.selected_teacher)[0]
        if data[1] not in SMS_DICT.keys():
            SMS_DICT[data[1]] = [data[0], [(self.period, self.cls)]]
            relief_dict[self.selected_teacher] = ["D{}P{}".format(self.day, self.period)]
        else:
            SMS_DICT[data[1]][1].append((self.period, self.cls))
            relief_dict[self.selected_teacher].append("D{}P{}".format(self.day, self.period))
        self.Lb1.delete(ACTIVE)
        self.current_selection = None
        # self.relief_assign.destroy()
        # AI.fit(self.cls, self.selected_teacher)

    def is_free(self, tid):
        if tid in relief_dict.keys() and "D{}P{}".format(self.day, self.period) in relief_dict[tid]:
            return False
        # noinspection SqlResolve
        a = DB.get(
            'SELECT `D{0}P{1}-S`,`D{0}P{1}-S` FROM Teachers WHERE Teacher_ID = {2}'.format(self.day,
                                                                                           self.period, tid))[0]

        return a == (None, None)


class Add_Teacher(Frame):
    def __init__(self):
        addTeacher = Tk()
        Frame.__init__(self, addTeacher)
        TimeTable = {}
        addTeacher.geometry("1024x576")
        addTeacher.wm_title('Add a New Teacher')

        ttk.Label(addTeacher, text='Add a New Teacher', font=FONT_Header).pack(side="top", pady=20)

        teacherDetails = Frame(addTeacher, height=20)

        ttk.Label(teacherDetails, text="Name : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Teacher_Name'] = ttk.Entry(teacherDetails)
        TimeTable['Teacher_Name'].pack(side="left", pady=10, padx=10, fill="x", expand=True)

        ttk.Label(teacherDetails, text="Teacher ID : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Teacher_ID'] = ttk.Entry(teacherDetails)
        TimeTable['Teacher_ID'].pack(side="left", pady=10, padx=10, fill="x", expand=True)

        ttk.Label(teacherDetails, text="Telephone Number : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Telephone_Number'] = ttk.Entry(teacherDetails)
        TimeTable['Telephone_Number'].pack(side="left", pady=10, padx=10, fill="x", expand=True)

        teacherDetails.pack(pady=20, fill="x")

        classTimeTable = Frame(addTeacher)
        ttk.Label(classTimeTable, text="Monday", font=NORM_FONT).grid(row=0, column=0, columnspan=3)
        ttk.Label(classTimeTable, text="Tuesday", font=NORM_FONT).grid(row=0, column=3, columnspan=3)
        ttk.Label(classTimeTable, text="Wednesday", font=NORM_FONT).grid(row=0, column=6, columnspan=3)
        ttk.Label(classTimeTable, text="Thursday", font=NORM_FONT).grid(row=0, column=9, columnspan=3)
        ttk.Label(classTimeTable, text="Friday", font=NORM_FONT).grid(row=0, column=12, columnspan=3)

        for i in range(0, 15, 3):
            ttk.Label(classTimeTable, text="Class", font=SMALL_FONT).grid(row=1, column=i, pady=5)
            ttk.Label(classTimeTable, text="Subject", font=SMALL_FONT).grid(row=1, column=i + 1, pady=5)

        D = 1
        P = 1
        for k in range(2, 10):
            for i in range(0, 15, 3):
                TimeTable['D{}P{}-C'.format(D, P)] = ttk.Entry(classTimeTable, justify='center', width=10)
                TimeTable['D{}P{}-C'.format(D, P)].grid(row=k, column=i, padx=3, pady=3, sticky=E)
                TimeTable['D{}P{}-S'.format(D, P)] = ttk.Entry(classTimeTable, justify='center', width=10)
                TimeTable['D{}P{}-S'.format(D, P)].grid(row=k, column=i + 1, padx=3, pady=3, sticky=W)
                ttk.Label(classTimeTable, font=NORM_FONT).grid(row=k, column=i + 2, padx=5, pady=3)
                D += 1
            P += 1
            D = 1

        classTimeTable.pack(pady=10, side=TOP, expand=True)

        ttk.Button(addTeacher, text="Submit", command=lambda: AddTeacherTODB(TimeTable)).pack(pady=50, padx=30,
                                                                                              side=RIGHT)

        addTeacher.mainloop()


class Modify_Teacher(Frame):
    def __init__(self):
        addTeacher = Tk()
        Frame.__init__(self, addTeacher)
        TimeTable = {}
        addTeacher.geometry("1024x576")
        addTeacher.wm_title('Modify a Teacher')

        ttk.Label(addTeacher, text='Modify a Teacher', font=FONT_Header).pack(side="top", pady=20)

        teacherDetails = Frame(addTeacher, height=20)

        ttk.Label(teacherDetails, text="Name : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Teacher_Name'] = ttk.Entry(teacherDetails)
        TimeTable['Teacher_Name'].pack(side="left", pady=10, padx=10, fill="x", expand=True)

        ttk.Label(teacherDetails, text="Teacher ID : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Teacher_ID'] = ttk.Entry(teacherDetails)
        TimeTable['Teacher_ID'].pack(side="left", pady=10, padx=10, fill="x", expand=True)

        ttk.Label(teacherDetails, text="Telephone Number : ", font=NORM_FONT).pack(side="left", pady=10, padx=10)
        TimeTable['Telephone_Number'] = ttk.Entry(teacherDetails)
        TimeTable['Telephone_Number'].pack(side="left", pady=10, padx=10, fill="x", expand=True)
        ttk.Button(teacherDetails, text="Search", command=lambda: findTeacher(TimeTable)).pack(padx=10, side=RIGHT)

        teacherDetails.pack(pady=20, fill="x")

        classTimeTable = Frame(addTeacher)
        ttk.Label(classTimeTable, text="Monday", font=NORM_FONT).grid(row=0, column=0, columnspan=3)
        ttk.Label(classTimeTable, text="Tuesday", font=NORM_FONT).grid(row=0, column=3, columnspan=3)
        ttk.Label(classTimeTable, text="Wednesday", font=NORM_FONT).grid(row=0, column=6, columnspan=3)
        ttk.Label(classTimeTable, text="Thursday", font=NORM_FONT).grid(row=0, column=9, columnspan=3)
        ttk.Label(classTimeTable, text="Friday", font=NORM_FONT).grid(row=0, column=12, columnspan=3)

        for i in range(0, 15, 3):
            ttk.Label(classTimeTable, text="Class", font=SMALL_FONT).grid(row=1, column=i, pady=5)
            ttk.Label(classTimeTable, text="Subject", font=SMALL_FONT).grid(row=1, column=i + 1, pady=5)

        D = 1
        P = 1
        for k in range(2, 10):
            for i in range(0, 15, 3):
                TimeTable['D{}P{}-C'.format(D, P)] = ttk.Entry(classTimeTable, justify='center', width=10)
                TimeTable['D{}P{}-C'.format(D, P)].grid(row=k, column=i, padx=3, pady=3, sticky=E)
                TimeTable['D{}P{}-S'.format(D, P)] = ttk.Entry(classTimeTable, justify='center', width=10)
                TimeTable['D{}P{}-S'.format(D, P)].grid(row=k, column=i + 1, padx=3, pady=3, sticky=W)
                ttk.Label(classTimeTable, font=NORM_FONT).grid(row=k, column=i + 2, padx=5, pady=3)
                D += 1
            P += 1
            D = 1

        classTimeTable.pack(pady=10, side=TOP, expand=True)

        ttk.Button(addTeacher, text="Update", command=lambda: updateTeacher(TimeTable)).pack(pady=50, padx=40,
                                                                                             side=RIGHT)
        ttk.Button(addTeacher, text="Delete", command=lambda: dropTeacher(TimeTable)).pack(pady=50, padx=0, side=RIGHT)
        addTeacher.mainloop()


try:
    if 1 <= current_day_of_week <= 5:
        app = Application()
        app.geometry("1024x576")
        app.mainloop()
except Exception as e:
    LOG.log.exception(e)
