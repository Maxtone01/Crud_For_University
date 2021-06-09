import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from PreDialog import PreDialog
import mysql.connector
global _connection
global _cursor


class MainWindow(QMainWindow):
    """
    MainWindow class, that was created to build main window and basic actions.
    """
    def __init__(self, *args, **kwargs):

        """
        This function was built to define some basic settings to main window, like window size, window title, etc.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Дізнатись результати")
        self.setWindowIcon(QtGui.QIcon("./images/results.png"))
        self.setMinimumSize(800, 600)
        self.create_table()
        self.actions()
        self.all_data()

    def connect_to_database(self):
        """
        Setting connection to the database.

        :return: database connection object.
        """
        global _connection
        _check_list = ['']

        _params = list()  # List, that will contain inside of himself information, that user will write till first open
        _file = open('connection.txt', 'r')  # Opening file with existing information about host and port parameters
        _list = [line.strip() for line in _file]  # Parsing document
        _params = _list

        # Check if file isn't empty. If true - taking information form file. If False - do else statement
        if (len(_params) != 0) and (len(_params) != len(_check_list)):
            _host = _params[0]
            _port = _params[1]
            _connection = mysql.connector.connect(
                host=_host,
                port=_port,
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                database=os.getenv('DATABASE'),
                charset="utf8"
            )
            return _connection.cursor()
        # If file is empty, user will write host and port information on his own.
        else:
            _values = self.get_connection()
            _host = _values[0]
            _port = _values[1]
            _connection = mysql.connector.connect(
                host=_host,
                port=_port,
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                database=os.getenv('DATABASE'),
                charset="utf8"
            )
            return _connection.cursor()

    def create_table(self):
        """
        Inside this function, i painted a table, to show data from database.

        :return: None
        """
        global _cursor
        _cursor = self.connect_to_database()

        self._table = QTableWidget()
        self.setCentralWidget(self._table)  # Setting central widget.

        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setCascadingSectionResizes(False)
        self._table.horizontalHeader().setSortIndicatorShown(False)
        self._table.horizontalHeader().setStretchLastSection(True)

        self._table.verticalHeader().setCascadingSectionResizes(False)
        self._table.verticalHeader().setStretchLastSection(False)

    def actions(self):
        """
        Function inside which i defined buttons for each action.

        :return: None
        """
        _toolbar = QToolBar()
        self.combo = QComboBox()
        _toolbar.setMovable(False)
        self.addToolBar(_toolbar)

        btn_refresh = QAction(QIcon("./images/lupa.png"), "Пошук вчителя", self)
        btn_refresh.triggered.connect(self.build_table_by_teacher)
        btn_refresh.setStatusTip("Пошук вчителя")
        _toolbar.addAction(btn_refresh)

        btn_choose = QAction(QIcon("./images/average.png"), "Середня оцінка", self)
        btn_choose.triggered.connect(self.get_average)
        btn_choose.setStatusTip("Середня оцінка")
        _toolbar.addAction(btn_choose)

        btn_result = QAction(QIcon("./images/results.png"), "Усі результати", self)
        btn_result.triggered.connect(self.all_data)
        btn_result.setStatusTip("Усі результати")
        _toolbar.addAction(btn_result)

        # Here i created _deps variable, that will contain inside herself information about departments, to fill
        # combo box.
        _deps = []
        _cursor.execute("select pname "
                        "from polls ")
        _pname = _cursor.fetchall()

        for i in _pname:
            _deps.append(i[0])

        _toolbar.addWidget(self.combo)
        self.combo.insertItems(1, _deps)
        self.combo.activated.connect(self.sort_by_department)

    def all_data(self):
        """
        Fill table with all data that was taken form database without filtration.

        :return: None
        """
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(("Рік та відділ опитування", "Вчитель", "Питання", "Оцінка"))
        _cursor.execute("select pname, tname, qtext, mark "
                        "from results_new, questions, teachers, polls "
                        "where results_new.kquestion = questions.kquestion "
                        "and questions.kquestion != 10 and results_new.kpoll = polls.kpoll "
                        "and results_new.kteacher = teachers.kteacher ")
        _row = _cursor.fetchall()
        self._table.setRowCount(0)
        for _row_number, _row_data in enumerate(_row):
            self._table.insertRow(_row_number)
            for _column_number, _teachers in enumerate(_row_data):
                self._table.setItem(_row_number, _column_number, QTableWidgetItem(str(_teachers)))

    def build_table_by_teacher(self):
        """
        Fill table with data from database using filtration by teacher name.

        :return: name of a teacher.
        """
        _values = list()
        _values = self.get_values()
        self._table.setColumnCount(4)

        self._table.setHorizontalHeaderLabels(("Рік та відділ опитування", "Вчитель", "Питання", "Оцінка"))
        self._tname = _values[0]
        _cursor.execute("select pname, tname, qtext, mark "
                        "from results_new, questions, teachers, polls "
                        "where results_new.kquestion = questions.kquestion "
                        "and questions.kquestion != 10 and results_new.kpoll = polls.kpoll "
                        "and results_new.kteacher = teachers.kteacher "
                        "and tname = '%s'"
                        "order by pname" % self._tname)
        _row = _cursor.fetchall()
        if not _row:
            #  if row is empty:
            raise QMessageBox.warning(QMessageBox(), "Помилка",
                                      "Перевірте, чи правильно ви ввели ПІБ, або ввели "
                                      "його не повністю.")
        else:
            self._table.setRowCount(0)
            for _row_number, _row_data in enumerate(_row):
                self._table.insertRow(_row_number)
                for _column_number, _teachers in enumerate(_row_data):
                    self._table.setItem(_row_number, _column_number, QTableWidgetItem(str(_teachers)))
        return self._tname

    def sort_by_department(self, text):
        """
        Sorting data by departments.

        :param text: takes values of departments, that was selected inside combo box
        :return: None
        """
        _depart = self.combo.itemText(text)
        _cursor.execute("select pname, tname, qtext, mark "
                        "from results_new, questions, teachers, polls "
                        "where results_new.kquestion = questions.kquestion "
                        "and questions.kquestion != 10 and results_new.kpoll = polls.kpoll "
                        "and results_new.kteacher = teachers.kteacher "
                        "and pname = '%s'"
                        "and tname = '%s'" % (_depart, self._tname))
        _row = _cursor.fetchall()
        self._table.setRowCount(0)
        for _row_number, _row_data in enumerate(_row):
            self._table.insertRow(_row_number)
            for _column_number, _teachers in enumerate(_row_data):
                self._table.setItem(_row_number, _column_number, QTableWidgetItem(str(_teachers)))

    def get_average(self):
        """
        Getting an average for teacher grade.

        :return: None
        """
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(("Рік та відділ опитування", "Вчитель", "Середня оцінка"))
        try:
            _cursor.execute(" select pname, tname, mark "
                            "from results_new, teachers, polls "
                            "where kquestion = 0 "
                            "and results_new.kteacher = teachers.kteacher "
                            "and results_new.kpoll = polls.kpoll "
                            "and tname = '%s'"
                            "order by pname" % self._tname)
            _row = _cursor.fetchall()
            self._table.setRowCount(0)
            for _row_number, _row_data in enumerate(_row):
                self._table.insertRow(_row_number)
                for _column_number, _teachers in enumerate(_row_data):
                    self._table.setItem(_row_number, _column_number, QTableWidgetItem(str(_teachers)))
        except:
            QMessageBox.warning(QMessageBox(), "Помилка", "Перевірте, чи отримали ви "
                                                          "свої попередні результати в таблиці.")

    @staticmethod
    def get_values():
        """
        Function to get teacher and department names from Dialog class.

        :return: name of teacher and name of department
        """
        _info = Dialog()
        _info.exec_()
        if _info.get_name():
            if _info.get_dep():
                return _info.get_name(), _info.get_dep()
        return None

    @staticmethod
    def get_connection():
        """
        Getting connection value from PreDialog class.

        :return: host and port info.
        """
        _info = PreDialog()
        _info.exec_()
        if _info.get_host():
            if _info.get_port():
                return _info.get_host(), _info.get_port()
        return None


class Dialog(QDialog):
    """
    Class that was created to set dialog window, that will open each time, while user will want to change
    or enter for the first time his name and set name of department.
    """
    def __init__(self, *args, **kwargs):
        """
        Setting basic functions for window.

        :param args:
        :param kwargs:
        """
        super(Dialog, self).__init__(*args, **kwargs)
        self.form_group_box()
        self.resize(300, 100)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.clicked.connect(self.accept)
        buttonBox.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Пошук")

    def form_group_box(self):
        """
        Inside this function, i set actions for group box.

        :return: None
        """
        _departments = []  # List with departments values.
        _teachers = []  # List with teachers values.

        _cursor.execute("select tname "
                        "from teachers ")
        _tnames = _cursor.fetchall()

        for i in _tnames:
            _teachers.append(i[0])

        _cursor.execute("select pname "
                        "from polls ")
        _row = _cursor.fetchall()

        for item in _row:
            _departments.append(item[0])

        self.formGroupBox = QGroupBox("Форма")
        layout = QFormLayout()

        self._text = QLineEdit()
        self._text.setPlaceholderText("Ви повинні ввести своє повне ПІБ.")
        completer = QCompleter(_teachers, self._text)
        self._text.setCompleter(completer)

        self._sbox = QSpinBox()

        self.combo = QComboBox()

        self.combo.addItems(_departments)

        layout.addRow(QLabel("Ім'я: "), self._text)
        self.formGroupBox.setLayout(layout)

    def get_dep(self):
        _depart = self.combo.currentText()
        return _depart

    def get_name(self):
        _tname = self._text.text()
        return _tname


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
