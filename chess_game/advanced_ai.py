import chess
import random

class AdvancedChessAI:
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    # Açılış veritabanı
    OPENINGS = {
        # Sicilya Savunması
        "Sicilian Defense": ["e2e4", "c7c5"],
        # Ruy Lopez
        "Ruy Lopez": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
        # İtalyan Oyunu
        "Italian Game": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
        # Kral Piyonu Oyunu
        "King's Pawn Game": ["e2e4", "e7e5"],
        # Kraliçe Gambiti
        "Queen's Gambit": ["d2d4", "d7d5", "c2c4"],
        # İngiliz Açılışı
        "English Opening": ["c2c4"],
        # Réti Açılışı
        "Reti Opening": ["g1f3", "d7d5", "c2c4"]
    }

    def __init__(self):
        self.max_depth = 5  # Daha derin arama
        self.opening_book = self.OPENINGS
        self.current_opening = None
        self.opening_moves = []
        
    def get_best_move(self, board):
        """En iyi hamleyi bul"""
        # Açılış kitaplığından hamle kontrolü
        opening_move = self._get_opening_move(board)
        if opening_move:
            return opening_move
            
        return self._get_calculated_move(board)

    def _get_opening_move(self, board):
        """Açılış kitaplığından hamle seç"""
        board_moves = [move.uci() for move in board.move_stack]
        
        # Eğer henüz bir açılış seçilmediyse ve oyun başındaysa
        if not self.current_opening and len(board_moves) < 2:
            self.current_opening = random.choice(list(self.OPENINGS.keys()))
            self.opening_moves = self.OPENINGS[self.current_opening].copy()
        
        # Eğer açılış devam ediyorsa
        if self.current_opening and self.opening_moves:
            next_move = self.opening_moves[0]
            # Hamlenin legal olduğundan emin ol
            try:
                move = chess.Move.from_uci(next_move)
                if move in board.legal_moves:
                    self.opening_moves.pop(0)
                    return move
            except:
                pass
            
        # Açılış bitmiş veya uygulanamamış
        self.current_opening = None
        self.opening_moves = []
        return None

    def _get_calculated_move(self, board):
        """Minimax algoritması ile en iyi hamleyi hesapla"""
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        legal_moves = list(board.legal_moves)
        # Hamleleri merkez kontrolü ve materyal değerine göre sırala
        legal_moves.sort(key=lambda move: self._move_sorting_value(board, move), reverse=True)
        
        for move in legal_moves:
            board.push(move)
            value = -self._minimax(board, self.max_depth - 1, -beta, -alpha, False)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)
            
        return best_move

    def _move_sorting_value(self, board, move):
        """Hamleleri sıralamak için değer hesapla"""
        value = 0
        
        # Taş değeri
        if board.is_capture(move):
            value += 10000
            
        # Merkez kontrolü
        to_square = move.to_square
        if to_square in [27, 28, 35, 36]:  # e4, d4, e5, d5
            value += 1000
            
        # Şah çekme
        board.push(move)
        if board.is_check():
            value += 5000
        board.pop()
        
        return value

    def _minimax(self, board, depth, alpha, beta, maximizing_player):
        """Gelişmiş minimax algoritması"""
        # Geçmiş beta kesme sayısı
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
                    break  # Beta kesme
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha kesme
            return value

    def _evaluate_position(self, board):
        """Gelişmiş pozisyon değerlendirmesi"""
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
                if piece.color:
                    value += piece_value
                else:
                    value -= piece_value
        
        # Merkez kontrolü (daha yüksek ağırlık)
        central_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        for square in central_squares:
            if board.piece_at(square) is not None:
                if board.piece_at(square).color:
                    value += 30
                else:
                    value -= 30
        
        # Piyon yapısı değerlendirmesi
        value += self._evaluate_pawn_structure(board)
        
        # Hareket özgürlüğü
        mobility = len(list(board.legal_moves))
        value += mobility * 0.1
        
        # Kale açık hatta mı?
        value += self._evaluate_rook_position(board)
        
        # Şah güvenliği
        value += self._evaluate_king_safety(board)
        
        return value if board.turn else -value

    def _evaluate_pawn_structure(self, board):
        """Piyon yapısını değerlendir"""
        value = 0
        
        # İzole piyonları cezalandır
        for file in range(8):
            white_pawns = 0
            black_pawns = 0
            for rank in range(8):
                square = rank * 8 + file
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    if piece.color:
                        white_pawns += 1
                    else:
                        black_pawns += 1
            
            # İzole piyonları kontrol et
            if file > 0 and file < 7:
                if white_pawns > 0 and not any(board.piece_at(square) and 
                    board.piece_at(square).piece_type == chess.PAWN and 
                    board.piece_at(square).color 
                    for square in [(rank * 8 + file - 1) for rank in range(8)] + 
                    [(rank * 8 + file + 1) for rank in range(8)]):
                    value -= 20  # İzole piyon cezası
                    
                if black_pawns > 0 and not any(board.piece_at(square) and 
                    board.piece_at(square).piece_type == chess.PAWN and 
                    not board.piece_at(square).color 
                    for square in [(rank * 8 + file - 1) for rank in range(8)] + 
                    [(rank * 8 + file + 1) for rank in range(8)]):
                    value += 20  # İzole piyon cezası
        
        return value

    def _evaluate_rook_position(self, board):
        """Kalelerin pozisyonunu değerlendir"""
        value = 0
        
        # Açık hatları kontrol et
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.ROOK:
                file = square % 8
                # Dosyada piyon var mı kontrol et
                pawns_in_file = 0
                for rank in range(8):
                    check_square = rank * 8 + file
                    check_piece = board.piece_at(check_square)
                    if check_piece and check_piece.piece_type == chess.PAWN:
                        pawns_in_file += 1
                
                if pawns_in_file == 0:  # Açık hat
                    if piece.color:
                        value += 30
                    else:
                        value -= 30
                    
        return value

    def _evaluate_king_safety(self, board):
        """Şah güvenliğini değerlendir"""
        value = 0
        
        # Her iki taraf için şah konumunu bul
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        if white_king_square is not None:
            # Beyaz şah için güvenlik değerlendirmesi
            if self._is_endgame(board):
                value += self._king_endgame_position_value(white_king_square, True)
            else:
                value += self._king_safety_value(board, white_king_square, True)
        
        if black_king_square is not None:
            # Siyah şah için güvenlik değerlendirmesi
            if self._is_endgame(board):
                value -= self._king_endgame_position_value(black_king_square, False)
            else:
                value -= self._king_safety_value(board, black_king_square, False)
        
        return value

    def _is_endgame(self, board):
        """Oyunun son aşamada olup olmadığını kontrol et"""
        # Vezirler yoksa veya her iki tarafın toplam materyal değeri düşükse son aşama
        white_material = sum(len(board.pieces(piece_type, chess.WHITE)) * value 
                           for piece_type, value in self.PIECE_VALUES.items() 
                           if piece_type != chess.KING)
        black_material = sum(len(board.pieces(piece_type, chess.BLACK)) * value 
                           for piece_type, value in self.PIECE_VALUES.items() 
                           if piece_type != chess.KING)
        
        return white_material < 1500 and black_material < 1500

    def _king_safety_value(self, board, king_square, is_white):
        """Şah güvenlik değeri hesapla"""
        value = 0
        file = king_square % 8
        rank = king_square // 8
        
        # Rok yapılmış mı kontrol et
        if is_white and rank == 0 and (file == 6 or file == 2):
            value += 100  # Rok bonusu
        elif not is_white and rank == 7 and (file == 6 or file == 2):
            value += 100  # Rok bonusu
            
        # Şahın etrafındaki kareleri kontrol et
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                new_file = file + dx
                new_rank = rank + dy
                
                if 0 <= new_file < 8 and 0 <= new_rank < 8:
                    square = new_rank * 8 + new_file
                    piece = board.piece_at(square)
                    if piece and piece.color == is_white:
                        value += 10  # Koruyucu taş bonusu
                        
        return value

    def _king_endgame_position_value(self, king_square, is_white):
        """Son aşamada şah pozisyon değeri"""
        file = king_square % 8
        rank = king_square // 8
        
        # Son aşamada şah merkeze yakın olmalı
        file_distance_from_center = abs(3.5 - file)
        rank_distance_from_center = abs(3.5 - rank)
        
        return -(file_distance_from_center + rank_distance_from_center) * 10
