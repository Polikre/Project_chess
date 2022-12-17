class GameState():
    def __init__(self):
        self.board = [
            ['bR9', 'bN9', 'bB9', 'bQ', 'bK', 'bB10', 'bN10', 'bR10'],
            ['bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7', 'bp8'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp1', 'wp2', 'wp3', 'wp4', 'wp5', 'wp6', 'wp7', 'wp8'],
            ['wR9', 'wN9', 'wB9', 'wQ', 'wK', 'wB10', 'wN10', 'wR10']]
        self.moveFunc = {'p': self.pawnMoves, 'R': self.rookMoves, 'N': self.knightMoves,
                         'B': self.bishopMoves, 'Q': self.queenMoves, 'K': self.kingMoves}
        self.whiteMove = True
        self.moveHist = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.promotePiece = "Q"
        self.CastlingRight = CastleRights(True, True, True, True)
        self.castleRightHist = [CastleRights(self.CastlingRight.wK_side, self.CastlingRight.bK_side,
                                             self.CastlingRight.wQ_side, self.CastlingRight.bQ_side)]

    def makeMove(self, move, prov):
        self.board[move.st_row][move.st_col] = "--"
        self.board[move.en_row][move.en_col] = move.home_sq
        self.moveHist.append(move)
        self.whiteMove = not self.whiteMove
        if move.home_sq == "wK":
            self.whiteKingLocation = (move.en_row, move.en_col)
        elif move.home_sq == "bK":
            self.blackKingLocation = (move.en_row, move.en_col)

        if move.isPawnPromotion:
            self.board[move.en_row][move.en_col] = move.home_sq[0] + self.promotePiece + move.home_sq[2]

        if move.isCastleMove:
            if move.en_col - move.st_col == 2:
                self.board[move.en_row][move.en_col - 1] = self.board[move.en_row][move.en_col + 1]
                self.board[move.en_row][move.en_col + 1] = "--"
            else:
                self.board[move.en_row][move.en_col + 1] = self.board[move.en_row][move.en_col - 2]
                self.board[move.en_row][move.en_col - 2] = "--"

        self.updateCasteRights(move, prov)
        self.castleRightHist.append(CastleRights(self.CastlingRight.wK_side, self.CastlingRight.bK_side, self.CastlingRight.wQ_side, self.CastlingRight.bQ_side))


    def undoMove(self):
        if len(self.moveHist) != 0:
            move = self.moveHist.pop()
            self.board[move.st_row][move.st_col] = move.home_sq
            self.board[move.en_row][move.en_col] = move.goal_sq
            self.whiteMove = not self.whiteMove
            if move.home_sq == "wK":
                self.whiteKingLocation = (move.st_row, move.st_col)
            elif move.home_sq == "bK":
                self.blackKingLocation = (move.st_row, move.st_col)
            self.castleRightHist.pop()
            self.CastlingRight = self.castleRightHist[-1]
            if move.isCastleMove:
                if move.en_col - move.st_col == 2:
                    self.board[move.en_row][move.en_col + 1] = self.board[move.en_row][move.en_col - 1]
                    self.board[move.en_row][move.en_col - 1] = "--"
                else:
                    self.board[move.en_row][move.en_col - 2] = self.board[move.en_row][move.en_col + 1]
                    self.board[move.en_row][move.en_col + 1] = "--"
            return move
        else:
            return False

    def updateCasteRights(self, move, prov):
        if prov == 0:
            if move.home_sq == "wK":
                self.CastlingRight.wK_side = False
                self.CastlingRight.wQ_side = False
            elif move.home_sq == "bK":
                self.CastlingRight.bK_side = False
                self.CastlingRight.bQ_side = False
            elif move.home_sq[:2] == "wR":
                if move.st_row == 7:
                    if move.st_col == 0:
                        self.CastlingRight.wQ_side = False
                    elif move.st_col == 7:
                        self.CastlingRight.wK_side = False
            elif move.home_sq[:2] == "bR":
                if move.en_row == 0:
                    if move.en_col == 0:
                        self.CastlingRight.bQ_side = False
                    elif move.en_col == 7:
                        self.CastlingRight.bK_side = False

            elif move.goal_sq[:2] == "wR":
                if move.en_row == 7:
                    if move.en_col == 0:
                        self.CastlingRight.wQ_side = False
                    elif move.en_col == 7:
                        self.CastlingRight.wK_side = False
            elif move.goal_sq[:2] == "bR":
                if move.en_row == 0:
                    if move.en_col == 0:
                        self.CastlingRight.bQ_side = False
                    elif move.en_col == 7:
                        self.CastlingRight.bK_side = False


    def getCorrectMoves(self, prov):
        tmpCastRight = CastleRights(self.CastlingRight.wK_side, self.CastlingRight.bK_side,
                                    self.CastlingRight.wQ_side, self.CastlingRight.bQ_side)
        moves = self.allCorrectMoves()
        if self.whiteMove:
            self.castleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.castleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i], 1)
            self.whiteMove = not self.whiteMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        self.CastlingRight = tmpCastRight
        self.castleRightHist[-1].bQ_side = self.CastlingRight.bQ_side
        self.castleRightHist[-1].wQ_side = self.CastlingRight.wQ_side
        self.castleRightHist[-1].wK_side = self.CastlingRight.wK_side
        self.castleRightHist[-1].bK_side = self.CastlingRight.bK_side
        return moves

    def inCheck(self):
        if self.whiteMove:
            return self.sqUndAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.sqUndAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def sqUndAttack(self, row, col):
        self.whiteMove = not self.whiteMove
        op_move = self.allCorrectMoves()
        self.whiteMove = not self.whiteMove
        for move in op_move:
            if move.en_row == row and move.en_col == col:
                return True
        return False

    def allCorrectMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                player = self.board[row][col][0]
                if (player == "w" and self.whiteMove) or (player == "b" and not self.whiteMove):
                    piec = self.board[row][col][1]
                    self.moveFunc[piec](row, col, moves)
        return moves

    def pawnMoves(self, row, col, moves):
        if self.whiteMove:
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                if self.board[row - 1][col - 1] == "--" and row == 3 and len(self.moveHist) != 0:
                    move = self.moveHist[-1]
                    if self.board[move.en_row][move.en_col][1] == "p" and move.st_row == 1:
                        if move.st_col + 1 == col and self.board[move.en_row][move.en_col][0] == "b":
                            moves.append(Move((row, col), (row - 1, col - 1), self.board))

            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                if self.board[row - 1][col + 1] == "--" and row == 3 and len(self.moveHist) != 0:
                    move = self.moveHist[-1]
                    if self.board[move.en_row][move.en_col][1] == "p" and move.st_row == 1:
                        if move.st_col - 1 == col and self.board[move.en_row][move.en_col][0] == "b":
                            moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                if self.board[row + 1][col - 1] == "--" and row == 4 and len(self.moveHist) != 0:
                    move = self.moveHist[-1]
                    if self.board[move.en_row][move.en_col][1] == "p" and move.st_row == 6:
                        if move.st_col - 1 == col and self.board[move.en_row][move.en_col][0] == "w":
                            moves.append(Move((row, col), (row + 1, col + 1), self.board))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                if self.board[row + 1][col - 1] == "--" and row == 4 and len(self.moveHist) != 0:
                    move = self.moveHist[-1]
                    if self.board[move.en_row][move.en_col][1] == "p" and move.st_row == 6:
                        if move.st_col + 1 == col and self.board[move.en_row][move.en_col][0] == "w":
                            moves.append(Move((row, col), (row + 1, col - 1), self.board))

    def rookMoves(self, row, col, moves):
        direct = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enm_color = "b" if self.whiteMove else "w"
        for d in direct:
            for i in range(1, 8):
                en_row = row + d[0] * i
                en_col = col + d[1] * i
                if 0 <= en_row < 8 and 0 <= en_col < 8:
                    en_piec = self.board[en_row][en_col]
                    if en_piec == "--":
                        moves.append(Move((row, col), (en_row, en_col), self.board))
                    elif en_piec[0] == enm_color:
                        moves.append(Move((row, col), (en_row, en_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def knightMoves(self, row, col, moves):
        kn_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        val_color = "w" if self.whiteMove else "b"
        for d in kn_moves:
            en_row = row + d[0]
            en_col = col + d[1]
            if 0 <= en_row < 8 and 0 <= en_col < 8:
                en_piec = self.board[en_row][en_col]
                if en_piec[0] != val_color:
                    moves.append(Move((row, col), (en_row, en_col), self.board))

    def bishopMoves(self, row, col, moves):
        direct = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enm_color = "b" if self.whiteMove else "w"
        for d in direct:
            for i in range(1, 8):
                en_row = row + d[0] * i
                en_col = col + d[1] * i
                if 0 <= en_row < 8 and 0 <= en_col < 8:
                    en_piec = self.board[en_row][en_col]
                    if en_piec == "--":
                        moves.append(Move((row, col), (en_row, en_col), self.board))
                    elif en_piec[0] == enm_color:
                        moves.append(Move((row, col), (en_row, en_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def kingMoves(self, row, col, moves):
        ki_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, - 1), (1, 0), (1, 1))
        val_color = "w" if self.whiteMove else "b"
        for i in range(8):
            en_row = row + ki_moves[i][0]
            en_col = col + ki_moves[i][1]
            if 0 <= en_row < 8 and 0 <= en_col < 8:
                en_piec = self.board[en_row][en_col]
                if en_piec[0] != val_color:
                    moves.append(Move((row, col), (en_row, en_col), self.board))

    def castleMoves(self, row, col, moves):
        if self.sqUndAttack(row, col):
            return
        if (self.whiteMove and self.CastlingRight.wK_side) or (not self.whiteMove and self.CastlingRight.bK_side):
            self.kingCastleMoves(row, col, moves)
        if (self.whiteMove and self.CastlingRight.wQ_side) or (not self.whiteMove and self.CastlingRight.bQ_side):
            self.queenCastleMoves(row, col, moves)

    def kingCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.sqUndAttack(row, col + 1) and not self.sqUndAttack(row, col + 2):
                moves.append(Move((row, col),  (row, col + 2), self.board, isCasltleMove=True))

    def queenCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.sqUndAttack(row, col - 1) and not self.sqUndAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCasltleMove=True))

    def queenMoves(self, row, col, moves):
        self.bishopMoves(row, col, moves)
        self.rookMoves(row, col, moves)


class CastleRights():
    def __init__(self, wK_side, bK_side, wQ_side, bQ_side):
        self.wK_side = wK_side
        self.bK_side = bK_side
        self.wQ_side = wQ_side
        self.bQ_side = bQ_side


class Move():

    numToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    letToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    rowToNum = {i: j for j, i in numToRow.items()}
    colToLet = {i: j for j, i in letToCol.items()}

    def __init__(self, stSq, enSq, board, isCasltleMove=False):
        self.st_row = stSq[0]
        self.st_col = stSq[1]
        self.en_row = enSq[0]
        self.en_col = enSq[1]
        self.home_sq = board[self.st_row][self.st_col]
        self.goal_sq = board[self.en_row][self.en_col]
        self.moveHash = self.st_row * 1000 + self.st_col * 100 + self.en_row * 10 + self.en_col
        self.isPawnPromotion = False
        self.enPassant = False
        if self.goal_sq == "--" and self.home_sq[1] == 'p' and abs(self.en_col - self.st_col) == 1:
            self.enPassant = True
        if (self.home_sq[:2] == "wp" and self.en_row == 0) or (self.home_sq[:2] == "bp" and self.en_row == 7):
            self.isPawnPromotion = True
        self.isCastleMove = isCasltleMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveHash == other.moveHash
        return False

    def ChessNot(self):
        tmp = ''
        goal_tmp = ''
        if abs(self.en_col - self.st_col) == 2 and self.home_sq[1] == "K":
            if self.en_col == 6:
                return "O-O"
            elif self.en_col == 2:
                return "O-O-O"
        if self.home_sq[1] != 'p':
            tmp = self.home_sq[1]
        else:
            goal_tmp = self.moveToNum(self.st_row, self.st_col)[0]
        if self.isPawnPromotion:
            return tmp + goal_tmp + "x" + self.moveToNum(self.en_row, self.en_col) + f"={GameState().promotePiece}"
        if self.goal_sq != "--" or self.enPassant:
            return tmp + goal_tmp + "x" + self.moveToNum(self.en_row, self.en_col)
        return tmp + self.moveToNum(self.en_row, self.en_col)

    def moveToNum(self, row, col):
        return self.colToLet[col] + self.rowToNum[row]

    def figures(self):
        return self.home_sq
