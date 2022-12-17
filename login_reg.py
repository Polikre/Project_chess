import sys
import random
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.Qt import *
import sqlite3
import main


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('project_s.ui', self)
        self.setWindowTitle('Login')
        self.userDataBase = sqlite3.connect('login.db')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        login = self.lineEdit.text()
        password = self.lineEdit1.text()
        self.acc = None
        alph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alph_izc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        fl = 0
        fl_pas = 0
        for i in login:
            if i not in alph:
                fl = 1
        for i in password:
            if i in alph_izc:
                fl_pas = 1
        if (not login) or (not password):
            QMessageBox.about(self, "Ошибка", "Вы не заполнили все поля")
            return
        elif len(login) < 4 or len(login) > 7:
            QMessageBox.about(self, "Ошибка", "Логин должен содержать не менее 4 и не более 7 символов")
            return
        elif len(password) < 8:
            QMessageBox.about(self, "Ошибка", "Пароль должен содержать не менее 8 символов")
            return
        elif fl:
            QMessageBox.about(self, "Ошибка", "Логин должен содержать только латинские символы")
            return
        elif fl_pas:
            QMessageBox.about(self, "Ошибка", "Пароль не должен содержать кириллицу")
            return
        res0 = self.userDataBase.execute(
            "SELECT * FROM USERS WHERE LOGIN = ?", (login,)).fetchall()
        res = self.userDataBase.execute(
            "SELECT * FROM USERS WHERE LOGIN = ? AND PASSWORD = ?", (login, password)).fetchall()
        if res != res0:
            QMessageBox.about(self, "Ошибка", "Неправильный пароль")
        else:
            self.userDataBase.cursor().execute(
                f"""INSERT INTO USERS(LOGIN, PASSWORD, WINS, DEFEATS, DRAWS, PICTURE) 
                VALUES('{login}', '{password}', 0, 0, 0, '0')""")
            self.userDataBase.commit()
            self.userDataBase.close()
            self.acc = playGame(login)
            self.acc.show()
            self.close()


class playGame(QMainWindow):
    def __init__(self, login):
        super().__init__()
        uic.loadUi('playgame.ui', self)
        self.setWindowTitle('Menu')
        self.login = login
        self.WHITE = None
        self.BLACK = None
        self.ranked = None
        self.pushButton_black.clicked.connect(self.black)
        self.pushButton_white.clicked.connect(self.white)
        self.pushButton_delete_account.clicked.connect(self.delete_account)
        self.pushButton_avatar.clicked.connect(self.avatar)
        self.pushButton_random.clicked.connect(self.random)
        self.pushButton_play.clicked.connect(self.play)
        self.pushButton_logout.clicked.connect(self.logout)
        self.pushButton_ranked.clicked.connect(self.rankedDo)
        self.pushButton_unranked.clicked.connect(self.unrankedDo)
        self.con = sqlite3.connect('login.db')
        self.cur = self.con.cursor()
        self.res = self.cur.execute(f"""SELECT WINS, DEFEATS, DRAWS, PICTURE FROM USERS WHERE LOGIN = 
'{self.login}'""").fetchall()[0]
        self.con.commit()
        _translate = QtCore.QCoreApplication.translate
        self.label_login.setText(_translate("MainWindow", f"""<html><head/><body><p align=\"center\"><span style=\" 
        font-size:64pt; font-weight:600;\">{self.login}</span></p></body></html>"""))
        self.label_wins.setText(_translate("MainWindow", f"""<html><head/><body><p><span style=\" 
        font-size:36pt; font-weight:600;\">{str(self.res[0])}</span></p></body></html>"""))
        self.label_defeats.setText(_translate("MainWindow", f"""<html><head/><body><p><span style=\" 
        font-size:36pt; font-weight:600;\">{str(self.res[1])}</span></p></body></html>"""))
        self.label_draws.setText(_translate("MainWindow",f"""<html><head/><body><p><span style=\" 
        font-size:36pt; font-weight:600;\">{str(self.res[2])}</span></p></body></html>"""))
        if self.res[3] != '0':
            self.pushButton_avatar.hide()
            self.pixmap = QPixmap(self.res[3])
            self.image = QLabel(self)
            self.image.resize(120, 120)
            self.image.move(550, 10)
            self.image.setScaledContents(True)
            self.image.setPixmap(self.pixmap)
            self.image.show()

    def rankedDo(self):
        self.ranked = True

    def unrankedDo(self):
        self.ranked = False

    def logout(self):
        self.con.commit()
        self.con.close()
        self.reg = MyWidget()
        self.reg.show()
        self.close()

    def delete_account(self):
        valid = QMessageBox.question(
            self, '', "Действительно удалить аккаунт?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.cur.execute(f"DELETE FROM USERS WHERE LOGIN LIKE '{self.login}'")
            self.logout()

    def avatar(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        if fname != "":
            self.pushButton_avatar.hide()
            self.pixmap = QPixmap(fname)
            self.image = QLabel(self)
            self.image.resize(120, 120)
            self.image.move(550, 10)
            self.image.setScaledContents(True)
            self.image.setPixmap(self.pixmap)
            self.image.show()
            self.cur.execute(f""" UPDATE USERS
                            SET PICTURE = '{fname}'
                            WHERE LOGIN =  '{self.login}' """)
            self.con.commit()

    def random(self):
        if random.randint(0, 1):
            self.white()
        else:
            self.black()

    def black(self):
        self.BLACK = True
        self.WHITE = False

    def white(self):
        self.BLACK = False
        self.WHITE = True

    def play(self):
        if self.BLACK is not None and self.WHITE is not None and self.ranked is not None:
            self.con.commit()
            self.con.close()
            self.game = main.Chess(self.WHITE, self.BLACK, self.login, self.ranked)
            self.game.show()
            self.close()
        else:
            if self.ranked is None:
                QMessageBox.about(self, "Ошибка", "Выберите тип партии")
            else:
                QMessageBox.about(self, "Ошибка", "Выберите цвет, которым будете играть")
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
