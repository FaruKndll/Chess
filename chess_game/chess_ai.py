import chess
import random

class ChessAI:
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    # Konum bazlı değerlendirme tabloları
    PAWN_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]

    KNIGHT_TABLE = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]

    BISHOP_TABLE = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ]

    ROOK_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]

    QUEEN_TABLE = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]

    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.max_depth = self._get_depth_by_difficulty()
        
    def _get_depth_by_difficulty(self):
        if self.difficulty == "easy":
            return 2
        elif self.difficulty == "medium":
            return 3
        else:  # hard
            return 4

    def get_best_move(self, board):
        """Verilen tahta durumu için en iyi hamleyi bul"""
        if self.difficulty == "easy":
            return self._get_easy_move(board)
        else:
            return self._get_calculated_move(board)

    def _get_easy_move(self, board):
        """Kolay seviye için basit bir hamle seç"""
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None

    def _get_calculated_move(self, board):
        """Minimax algoritması ile en iyi hamleyi hesapla"""
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            value = -self._minimax(board, self.max_depth - 1, -beta, -alpha, False)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)
            
        return best_move

    def _minimax(self, board, depth, alpha, beta, maximizing_player):
        """Minimax algoritması ile pozisyonu değerlendir"""
        if depth == 0 or board.is_game_over():
            return self._evaluate_position(board)
            
        if maximizing_player:
            value = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def _evaluate_position(self, board):
        """Pozisyonu değerlendir"""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        value = 0
        # Materyal değerlendirmesi
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                piece_value = self.PIECE_VALUES[piece.piece_type]
                
                # Konum değerlendirmesi
                position_value = 0
                if piece.piece_type == chess.PAWN:
                    position_value = self.PAWN_TABLE[square if piece.color else 63 - square]
                elif piece.piece_type == chess.KNIGHT:
                    position_value = self.KNIGHT_TABLE[square if piece.color else 63 - square]
                elif piece.piece_type == chess.BISHOP:
                    position_value = self.BISHOP_TABLE[square if piece.color else 63 - square]
                elif piece.piece_type == chess.ROOK:
                    position_value = self.ROOK_TABLE[square if piece.color else 63 - square]
                elif piece.piece_type == chess.QUEEN:
                    position_value = self.QUEEN_TABLE[square if piece.color else 63 - square]
                
                if piece.color:
                    value += piece_value + position_value * 0.1
                else:
                    value -= piece_value + position_value * 0.1
                    
        # Merkez kontrolü
        central_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        for square in central_squares:
            if board.piece_at(square) is not None:
                if board.piece_at(square).color:
                    value += 10
                else:
                    value -= 10
                    
        # Hareket özgürlüğü
        value += len(list(board.legal_moves)) * 0.1
        
        return value if board.turn else -value
