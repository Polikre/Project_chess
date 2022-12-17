import random

pieceScore = {"K": 0, "Q": 10, "p": 1, "B": 3, "N": 3, "R": 5}
checkmate = 9999
stalemate = 0
prov = 1


def randomMoves(valMoves):
    return valMoves[random.randint(0, len(valMoves) - 1)]


def bestMoves(gs, valMoves):
    turnDeterminant = 1 if gs.whiteMove else -1
    opponentScore = checkmate
    bMove = None
    random.shuffle(valMoves)
    for pMove in valMoves:
        gs.makeMove(pMove, prov)
        opponentsMoves = gs.getCorrectMoves(prov)
        max_opponentScore = - checkmate
        for opMove in opponentsMoves:
            gs.makeMove(opMove, prov)
            if gs.checkmate:
                score = -turnDeterminant * checkmate
            elif gs.stalemate:
                score = stalemate
            else:
                score = -turnDeterminant * scoredMaterial(gs.board)
            if score > max_opponentScore:
                max_opponentScore = score
            gs.undoMove()
        if opponentScore > max_opponentScore:
            opponentScore = max_opponentScore
            bMove = pMove
        gs.undoMove()
    return bMove


def scoredMaterial(board):
    score = 0
    for row in board:
        for sq in row:
            if sq[0] == "w":
                score += pieceScore[sq[1]]
            elif sq[0] == "b":
                score -= pieceScore[sq[1]]
    return score