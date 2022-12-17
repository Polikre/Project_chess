from PyQt5.Qt import *
from PyQt5.QtGui import QPixmap, QPainter, QColor, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QSizePolicy,  QGridLayout
from PyQt5.QtCore import Qt
import Engine
import ComputerMove
import sqlite3
import login_reg
import csv

WIGHT = 512
HEIGHT = 512
MOVE_HIST_WIGHT = 512
MOVE_HIST_HEIGHT = 256
SIZE = 8
SQ_S = HEIGHT // SIZE
IMAGES = {}
DELAY = 50
GAME = False


class Chess(QWidget):
    def __init__(self, white, black, login, ranked):
        super().__init__()
        self.initUI(white, black, login, ranked)

    def initUI(self, white, black, login, ranked):
        global GAME
        self.data = []
        self.ranked = ranked
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(HEIGHT, 0, HEIGHT + MOVE_HIST_HEIGHT, MOVE_HIST_WIGHT - 60))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        _translate = QCoreApplication.translate
        self.pushButton_backMenu = QPushButton(self)
        self.pushButton_backMenu.setGeometry(QRect(HEIGHT, MOVE_HIST_WIGHT - 60, 131, 61))
        self.pushButton_backMenu.setObjectName("backMenu")
        self.pushButton_backMenu.setText(_translate("MainWindow", "К профилю"))
        self.pushButton_backMenu.clicked.connect(self.logout)

        self.pushButton_undoMove = QPushButton(self)
        self.pushButton_undoMove.setGeometry(QRect(HEIGHT + 125, MOVE_HIST_WIGHT - 60, 131, 61))
        self.pushButton_undoMove.setObjectName("undoMove")
        self.pushButton_undoMove.setText(_translate("MainWindow", "Отменить ход"))
        self.pushButton_undoMove.clicked.connect(self.backMove)
        if self.ranked:
            self.pushButton_undoMove.hide()

        self.tmp = ""
        self.login = login
        self.setWindowTitle('Chess')
        self.move_anim = []
        self.en_pass = None
        self.resize(HEIGHT + MOVE_HIST_HEIGHT, WIGHT)
        self.sqSelected = ()
        self.gs = Engine.GameState()
        self.correctMoves = self.gs.getCorrectMoves(0)
        self.moveMake = False
        self.playerClicks = []
        self.loadImages()
        self.move = Engine.Move((0, 0), (0, 0), self.gs.board)
        self.move_val = Engine.Move((0, 0), (0, 0), self.gs.board)
        self.drawPiece(self.gs.board)
        self.choice = False
        self.moved = False
        self.gameOver = False
        self.playerOne = white
        self.playerTwo = black
        self.counter = 0
        self.hTurn = (self.gs.whiteMove and self.playerOne) or (not self.gs.whiteMove and self.playerTwo)
        GAME = True
        if not self.gameOver and not self.hTurn:
            self.mousePressEvent(None)

    def mousePressEvent(self, event):
        move = self.move_val
        if not self.gameOver and not self.hTurn:
            move = ComputerMove.bestMoves(self.gs, self.correctMoves)
            if move is None:
                move = ComputerMove.randomMoves(self.correctMoves)
        else:
            if self.hTurn and not self.gameOver:
                x, y = event.x(), event.y()
                col = x // SQ_S
                row = y // SQ_S
                if self.sqSelected == (row, col) or col >= 8:
                    self.sqSelected = ()
                    self.playerClicks = []
                else:
                    self.sqSelected = (row, col)
                    self.playerClicks.append(self.sqSelected)
                if len(self.playerClicks) == 2:
                    self.choice = False
                    move = Engine.Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
                    self.sqSelected = ()
                    self.playerClicks = []
                else:
                    self.choice = True

        for i in range(len(self.correctMoves)):
            if move == self.correctMoves[i]:
                self.gs.makeMove(move, 0)
                self.MoveHistUpdate()
                self.move = move
                self.hTurn = (self.gs.whiteMove and self.playerOne) or (not self.gs.whiteMove and self.playerTwo)
                self.moveMake = True
                self.moved = True
                if move.home_sq != "--":
                    self.movedAnimation(move.home_sq, move.en_col, move.en_row)
                    if move.goal_sq != "--":
                        IMAGES[move.goal_sq].hide()
                    if move.goal_sq == "--" and move.home_sq[1] == 'p' and abs(move.en_col - move.st_col) == 1:
                        if self.gs.board[move.en_row + 1][move.en_col][1] == "p":
                            IMAGES[self.gs.board[move.en_row + 1][move.en_col]].hide()
                            self.en_pass = self.gs.board[move.en_row + 1][move.en_col]
                            self.gs.board[move.en_row + 1][move.en_col] = "--"
                        elif self.gs.board[move.en_row - 1][move.en_col][1] == "p":
                            IMAGES[self.gs.board[move.en_row - 1][move.en_col]].hide()
                            self.en_pass = self.gs.board[move.en_row + 1][move.en_col]
                            self.gs.board[move.en_row - 1][move.en_col] = "--"
                if move.isPawnPromotion:
                    tm = self.gs.board[move.en_row][move.en_col]
                    IMAGES[tm[0] + 'p' + tm[2]].hide()
                    self.movedAnimation(tm, move.en_col, move.en_row)
                    IMAGES[tm].show()
                if abs(move.en_col - move.st_col) == 2 and move.home_sq[1] == "K":
                    if move.en_col - move.st_col > 0:
                        self.gs.board[move.en_row][move.en_col - 1] = move.home_sq[0] + 'R' + '10'
                        self.gs.board[move.en_row][7] = "--"
                        self.movedAnimation(move.home_sq[0] + 'R' + '10', move.en_col - 1, move.en_row)
                    else:
                        self.gs.board[move.en_row][move.en_col + 1] = move.home_sq[0] + 'R' + '9'
                        self.gs.board[move.en_row][0] = "--"
                        self.movedAnimation(move.home_sq[0] + 'R' + '9', move.en_col + 1, move.en_row)

        if self.moveMake:
            self.correctMoves = self.gs.getCorrectMoves(0)
            self.moveMake = False

        if self.gs.stalemate or self.gs.checkmate:
            self.gameOver = True
            if self.gs.stalemate:
                text = "Ничья"
                self.tmp = 'DRAWS'
            else:
                if self.hTurn:
                    text = "Вы проиграли"
                    self.tmp = "DEFEATS"
                else:
                    text = "Вы победили"
                    self.tmp = "WINS"
            self.endGameMessage(text)

        self.repaint()
        if not self.gameOver and not self.hTurn:
            self.mousePressEvent(event)

    def endGameMessage(self, text):
        QMessageBox.about(self, "Конец игры", text)
        self.update_stats(self.tmp)

    def update_stats(self, tmp):
        if self.ranked:
            con = sqlite3.connect('login.db')
            cur = con.cursor()
            cur.execute(f""" UPDATE USERS
                                    SET {tmp} = {tmp} + 1
                                    WHERE LOGIN =  '{self.login}' """)
            con.commit()
            con.commit()

    def leaveGame(self):
        self.plGa = login_reg.playGame(self.login)
        self.plGa.show()
        self.close()

    def logout(self):
        if not self.gameOver and self.ranked:
            valid = QMessageBox.question(
                self, 'Выход в меню', '''Игра ещё не завершилась.Вы проиграете, если сейчас вернетесь в меню.
                Хотите продолжить?''',
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                self.update_stats("DEFEATS")
                self.leaveGame()
        else:
            self.leaveGame()

    def backMove(self):
        move = self.gs.undoMove()
        self.MoveHistUpdate()
        if len(self.gs.moveHist) != 0:
            self.move = self.gs.moveHist[-1]
        else:
            self.move = self.move_val
        self.repaint()
        if move and move.home_sq != "--":
            IMAGES[move.home_sq].move(move.st_col * SQ_S, move.st_row * SQ_S)
            if move.goal_sq != "--":
                IMAGES[move.goal_sq].show()
            if move.goal_sq == "--" and move.home_sq[1] == 'p' and abs(move.en_col - move.st_col) == 1:
                if move.st_row == 4:
                    self.gs.board[move.en_row - 1][move.en_col] = self.en_pass
                    IMAGES[self.gs.board[move.en_row - 1][move.en_col]].show()
                elif move.st_row == 3:
                    self.gs.board[move.en_row + 1][move.en_col] = self.en_pass
                    IMAGES[self.gs.board[move.en_row + 1][move.en_col]].show()
            if move.isPawnPromotion:
                tm = move.home_sq
                IMAGES[tm].show()
                IMAGES[tm[0] + self.gs.promotePiece + tm[2]].hide()
            if abs(move.en_col - move.st_col) == 2 and move.home_sq[1] == "K":
                if move.en_col - move.st_col > 0:
                    self.gs.board[move.en_row][move.en_col - 1] = "--"
                    self.gs.board[move.en_row][7] = move.home_sq[0] + 'R' + '10'
                    IMAGES[move.home_sq[0] + 'R' + '10'].move((SIZE - 1) * SQ_S, move.en_row * SQ_S)
                else:
                    self.gs.board[move.en_row][move.en_col + 1] = "--"
                    self.gs.board[move.en_row][0] = move.home_sq[0] + 'R' + '9'
                    IMAGES[move.home_sq[0] + 'R' + '9'].move(0, move.en_row * SQ_S)

        self.correctMoves = self.gs.getCorrectMoves(0)
        self.moveMake = False


    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawBoard(qp)
        self.drawMoveHist(qp)
        if self.choice:
            self.glowingSquares(qp)
        if self.moved:
            fl = 0
            if (self.move.st_col == self.move.st_row) and (self.move.en_row == self.move.en_col):
                if (self.move.st_col == self.move.en_row) and (self.move.st_col == 0):
                    fl = 1
            if not fl:
                self.moved_goal_sq(qp, self.move.st_row, self.move.st_col)
                self.moved_goal_sq(qp, self.move.en_row, self.move.en_col)
        qp.end()

    def glowingSquares(self, qp):
        if self.sqSelected != ():
            row, col = self.sqSelected[0], self.sqSelected[1]
            if self.gs.board[row][col][0] == ("w" if self.gs.whiteMove else "b"):
                qp.setBrush(QColor(66, 170, 255))
                qp.drawRect(col * SQ_S, SQ_S * row, SQ_S + 1, SQ_S + 1)
                for move in self.correctMoves:
                    if move.st_row == row and move.st_col == col:
                        if move.en_row % 2 == move.en_col % 2:
                            qp.setBrush(QColor(127, 255, 0))
                        else:
                            qp.setBrush(QColor(50, 205, 50))
                        qp.drawRect(move.en_col * SQ_S, move.en_row * SQ_S, SQ_S + 1, SQ_S + 1)

    def drawBoard(self, qp):
        for row in range(SIZE):
            for col in range(SIZE):
                if row % 2 == col % 2:
                    qp.setBrush(QColor(235, 235, 211))
                else:
                    qp.setBrush(QColor(125, 147, 92))
                qp.drawRect(int(col * SQ_S), int(row * SQ_S), int((col + 1) * SQ_S), int((row + 1) * SQ_S))

    def drawPiece(self, board):
        for row in range(SIZE):
            for col in range(SIZE):
                piec = board[row][col]
                if piec != "--":
                    IMAGES[piec].move(SQ_S * col, SQ_S * row)
                    IMAGES[piec].show()

    def moved_goal_sq(self, qp, row, col):
        if row % 2 == col % 2:
            qp.setBrush(QColor(247, 247, 149))
        else:
            qp.setBrush(QColor(190, 202, 89))
        qp.drawRect(col * SQ_S, row * SQ_S, SQ_S + 1, SQ_S + 1)\


    def movedAnimation(self, home_sq,en_col, en_row):
        IMAGES[home_sq].move(SQ_S * en_col, SQ_S * en_row)


    def drawMoveHist(self, qp):
        qp.setBrush(QColor(0, 0, 0))
        qp.drawRect(HEIGHT, 0, HEIGHT + MOVE_HIST_HEIGHT, MOVE_HIST_WIGHT)

    def MoveHistUpdate(self):
        if len(self.gs.moveHist) != 0:
            data = []
            for i in range(len(self.gs.moveHist)):
                txt = self.gs.moveHist[i].ChessNot()
                if i % 2:
                    data[-1]["BlackMove"] = txt
                else:
                    data.append({"WhiteMove": txt})
            with open('MoveHist.csv', 'w', newline='', encoding="utf8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=list(data[0].keys()),
                    delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for d in data:
                    writer.writerow(d)
            self.loadTable()

    def loadTable(self):
        with open('MoveHist.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()


    def loadImages(self):
        pieces_pov = ['bR', 'bN', 'bB', 'bQ1', 'wR', 'wN', 'wB', 'wQ1', 'wp', 'bp']
        izc = ['wK', 'bK', 'wQ', 'bQ', 'bR9', 'bR10', 'bN9', 'bN10', 'bB9', 'bB10',
               'wR9', 'wR10', 'wN9', 'wN10', 'wB9', 'wB10']
        pieces = pieces_pov + izc
        for piec in pieces:
            if piec not in izc:
                for i in range(1, 9):
                    piec0 = piec[:2] + str(i)
                    self.pixmap = QPixmap(f"images/{piec0}.png")
                    self.image = QLabel(self)
                    self.image.resize(SQ_S + 1, SQ_S + 1)
                    self.image.move(0, 0)
                    self.image.setScaledContents(True)
                    self.image.setPixmap(self.pixmap)
                    self.image.hide()
                    IMAGES[piec0] = self.image
            else:
                self.pixmap = QPixmap(f"images/{piec}.png")
                self.image = QLabel(self)
                self.image.resize(SQ_S + 1, SQ_S + 1)
                self.image.move(0, 0)
                self.image.setScaledContents(True)
                self.image.setPixmap(self.pixmap)
                self.image.hide()
                IMAGES[piec] = self.image
