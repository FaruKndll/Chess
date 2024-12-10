import chess
import tkinter as tk
from tkinter import messagebox
import random
from piece_loader import PieceLoader
import time
from chess_ai import ChessAI
from advanced_ai import AdvancedChessAI

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Satranç Oyunu")
        self.board = chess.Board()
        self.pieces = PieceLoader(size=50)
        self.move_history = []
        self.selected_square = None
        self.dragging = False
        self.drag_image_label = None
        self._current_drag_image = None
        self.possible_moves = []
        self.game_stats = {
            'white_captures': [],
            'black_captures': [],
            'move_count': 0,
            'check_count': 0,
            'game_duration': 0,
            'start_time': None
        }
        self.difficulty = "easy"
        self.ai = None
        self.show_main_menu()

    def get_piece_symbol(self, piece):
        if piece is None:
            return None
            
        color = 'w' if piece.color == chess.WHITE else 'b'
        piece_type = piece.symbol().lower()
        return f"{color}{piece_type}"
        
    def update_board(self):
        """Tahtayı güncelle"""
        if not hasattr(self, 'buttons') or not self.buttons:
            return
            
        for row in range(8):
            for col in range(8):
                square = (7-row) * 8 + col
                piece = self.board.piece_at(square)
                button = self.buttons[row][col]
                
                if button is None:
                    continue
                    
                frame = button.master
                if frame is None:
                    continue
                
                # Temel arka plan rengini ayarla
                base_color = "#ecf0f1" if (row + col) % 2 == 0 else "#34495e"
                button.configure(bg=base_color)
                frame.configure(bg=base_color)
                
                # Seçili kare için ince kenarlık
                if square == self.selected_square:
                    frame.configure(highlightbackground="#27ae60", highlightthickness=2)
                # Olası hamleler için gösterge
                elif square in [move.to_square for move in self.possible_moves]:
                    if self.board.piece_at(square):
                        button.configure(bg="#e74c3c")
                    else:
                        for widget in button.winfo_children():
                            if isinstance(widget, tk.Canvas):
                                widget.destroy()
                        
                        # Daha büyük ve belirgin gösterge
                        indicator = tk.Canvas(button, width=16, height=16,
                                           bg=base_color, highlightthickness=0)
                        indicator.create_oval(2, 2, 14, 14,
                                           fill="#3498db",
                                           outline="#ecf0f1",
                                           width=1)
                        indicator.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    frame.configure(highlightthickness=0)
                    # Eski göstergeleri temizle
                    for widget in button.winfo_children():
                        if isinstance(widget, tk.Canvas):
                            widget.destroy()
                
                # Taş görüntüsünü ayarla
                piece_symbol = self.get_piece_symbol(piece)
                if piece_symbol:
                    piece_image = self.pieces.get_piece_image(piece_symbol)
                    if piece_image:
                        button.configure(image=piece_image, width=50, height=50)
                        button.image = piece_image  # Referansı sakla
                else:
                    button.configure(image="", width=50, height=50)
                    
    def is_valid_move(self, move):
        """Hamlenin geçerli olup olmadığını kontrol et"""
        if move is None:
            return False
        return any(m.from_square == move.from_square and 
                  m.to_square == move.to_square for m in self.board.legal_moves)

    def on_square_click(self, event, row, col):
        """Kareye tıklandığında"""
        square = (7-row) * 8 + col
        piece = self.board.piece_at(square)
        
        # Eğer zaten bir taş seçiliyse ve aynı kareye tıklandıysa seçimi iptal et
        if self.selected_square == square:
            self.reset_selection()
            return
        
        # Eğer bir taş seçiliyse ve başka bir kareye tıklandıysa
        if self.selected_square is not None:
            # Hedef karedeki taş bizim taşımızsa, yeni taşı seç
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self._current_drag_image = self.pieces.get_piece_image(self.get_piece_symbol(piece))
                self.show_possible_moves(square)
                return
            
            # Değilse hamle yapmayı dene
            move = chess.Move(self.selected_square, square)
            if self.is_valid_move(move):
                self.make_move(move)
            self.reset_selection()
            return
            
        # Eğer tıklanan karede bir taş varsa ve sırası gelen oyuncunun taşıysa
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self._current_drag_image = self.pieces.get_piece_image(piece)
            self.show_possible_moves(square)
            self.dragging = False  # Sadece tıklama ile seçim yapıldığında sürükleme modunu kapatıyoruz

    def on_square_drag(self, event, row, col):
        """Kare üzerinde sürükleme"""
        if self.dragging and self.selected_square is not None and self._current_drag_image:
            # Sürükleme görüntüsünü güncelle
            if not self.drag_image_label:
                self.drag_image_label = tk.Label(self.window, image=self._current_drag_image)
                self.drag_image_label.lift()
            
            # Fare pozisyonuna göre görüntüyü güncelle
            x = event.x_root - self.window.winfo_rootx() - 25
            y = event.y_root - self.window.winfo_rooty() - 25
            self.drag_image_label.place(x=x, y=y)

    def on_square_release(self, event, row, col):
        """Kare üzerinde bırakma"""
        if not self.dragging or self.selected_square is None:
            return

        # Sürükleme görüntüsünü temizle
        if self.drag_image_label:
            self.drag_image_label.destroy()
            self.drag_image_label = None

        target_square = (7-row) * 8 + col
        
        # Eğer aynı kareye bırakıldıysa işlem yapma
        if target_square == self.selected_square:
            self.dragging = False
            return

        # Hamleyi oluştur
        move = chess.Move(self.selected_square, target_square)
        
        # Piyon terfisi kontrolü
        piece = self.board.piece_at(self.selected_square)
        if piece and piece.piece_type == chess.PAWN:
            if (piece.color and target_square >= 56) or (not piece.color and target_square < 8):
                if self.is_valid_move(move):
                    self.handle_pawn_promotion(move)
                    self.reset_selection()
                    return

        # Normal hamle
        if self.is_valid_move(move):
            self.make_move(move)
        
        self.reset_selection()
        self.clear_possible_moves()

    def make_move(self, move):
        """Hamleyi yap ve gerekli güncellemeleri gerçekleştir"""
        # Piyon terfisi kontrolü
        if self.is_pawn_promotion(move):
            move = self.handle_pawn_promotion(move)
            if not move:  # Kullanıcı terfi penceresini kapattıysa
                return False

        # Taşın alınıp alınmadığını kontrol et
        captured_piece = self.board.piece_at(move.to_square)
        
        # Hamleyi yap
        san_move = self.board.san(move)
        
        # Eğer bir taş alındıysa istatistiklere ekle
        if captured_piece:
            piece_symbol = self.get_piece_unicode(captured_piece)
            if self.board.turn:  # Beyaz hamle yapıyorsa
                self.game_stats['white_captures'].append(piece_symbol)
            else:  # Siyah hamle yapıyorsa
                self.game_stats['black_captures'].append(piece_symbol)
            self.update_capture_labels()

        self.board.push(move)
        
        # İstatistikleri güncelle
        self.game_stats['move_count'] += 1
        if self.board.is_check():
            self.game_stats['check_count'] += 1
            self.check_label.config(text="ŞAH!")
        else:
            self.check_label.config(text="")
        
        # Hamle geçmişine ekle
        move_number = (len(self.move_history) // 2) + 1
        if len(self.move_history) % 2 == 0:
            history_text = f"{move_number}. {san_move}"
        else:
            history_text = f"    {san_move}"
        self.move_history.append(san_move)
        self.history_listbox.insert(tk.END, history_text)
        self.history_listbox.see(tk.END)

        # Tahtayı ve durumu güncelle
        self.update_board()
        self.update_status()
        self.update_game_status()
        
        # Eğer oyun bitmemişse ve sıra siyahtaysa AI hamle yapsın
        if not self.board.is_game_over() and self.board.turn == chess.BLACK:
            self.window.after(500, self.make_ai_move)  # 500ms sonra AI hamle yapsın

    def reset_selection(self):
        """Seçim ve sürükleme durumunu sıfırla"""
        self.selected_square = None
        self.dragging = False
        self._current_drag_image = None
        self.clear_possible_moves()
    
    def show_possible_moves(self, square):
        """Seçili taşın olası hamlelerini göster"""
        self.possible_moves = [move for move in self.board.legal_moves if move.from_square == square]
        self.update_board()
    
    def clear_possible_moves(self):
        """Olası hamle göstergelerini temizle"""
        self.possible_moves = []
        self.update_board()
    
    def square_to_coords(self, square):
        """Kare numarasını satranç koordinatlarına çevirir (örn: 0 -> a8)"""
        file_letter = chr(ord('a') + (square % 8))
        rank_number = 8 - (square // 8)  # 8'den başlayıp aşağı doğru giden koordinat
        return f"{file_letter}{rank_number}"

    def evaluate_position(self, board):
        """Pozisyonu değerlendir"""
        if board.is_checkmate():
            return -10000 if board.turn else 10000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        # Oyun fazını belirle
        total_pieces = len(board.piece_map())
        is_endgame = total_pieces <= 10
        
        # Taş değerleri
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        score = 0
        pieces = board.piece_map()
        
        # Tehdit altındaki taşları ve karşı hamle fırsatlarını değerlendir
        for square, piece in pieces.items():
            if piece.color != board.turn:  # Rakip taşları değerlendir
                continue
                
            value = piece_values[piece.piece_type]
            attackers = board.attackers(not piece.color, square)
            defenders = board.attackers(piece.color, square)
            
            # Taş tehdit altında mı kontrol et
            if attackers:
                min_attacker_value = min(piece_values[board.piece_at(attacker).piece_type] 
                                      for attacker in attackers)
                max_defender_value = max([piece_values[board.piece_at(defender).piece_type] 
                                      for defender in defenders] or [0])
                
                # Karşı atak fırsatlarını ara
                counter_attacks = []
                for move in board.legal_moves:
                    if move.from_square == square:
                        # Hamle bir taş yiyor mu?
                        if board.piece_at(move.to_square):
                            target_value = piece_values[board.piece_at(move.to_square).piece_type]
                            
                            # Hamleden sonraki durumu simüle et
                            board.push(move)
                            future_attackers = board.attackers(not piece.color, move.to_square)
                            future_defenders = board.attackers(piece.color, move.to_square)
                            is_safe_after_move = not future_attackers or (future_defenders and 
                                               len(future_defenders) >= len(future_attackers))
                            board.pop()
                            
                            counter_attacks.append((target_value, is_safe_after_move))
                
                # Karşı atak stratejisi
                if counter_attacks:
                    best_target_value = max(ca[0] for ca in counter_attacks)
                    is_any_safe_attack = any(ca[1] for ca in counter_attacks)
                    
                    # Eğer değerli bir karşı atak yapılabiliyorsa
                    if best_target_value >= min_attacker_value:
                        if is_any_safe_attack:
                            score += best_target_value * 2  # Güvenli karşı atağa yüksek bonus
                        else:
                            score += best_target_value  # Riskli ama değerli karşı atak
                            
                    # Değerli taşı koruma stratejisi
                    elif value > min_attacker_value:
                        if defenders:
                            if max_defender_value >= min_attacker_value:
                                score += value  # Savunulabilir değerli taş
                            else:
                                score -= value // 2  # Zayıf savunulan değerli taş
                        else:
                            score -= value  # Savunmasız değerli taş
                            
                    # Değersiz taşla saldırı stratejisi
                    else:
                        if best_target_value > value:
                            score += best_target_value - value  # Karlı değişim
                            
            # Normal hamle değerlendirmesi
            for move in board.legal_moves:
                if move.from_square == square:
                    # Taş yeme hamlesi
                    if board.piece_at(move.to_square):
                        target_value = piece_values[board.piece_at(move.to_square).piece_type]
                        
                        # Hamleden sonraki güvenliği kontrol et
                        board.push(move)
                        is_safe = not board.attackers(not piece.color, move.to_square) or \
                                bool(board.attackers(piece.color, move.to_square))
                        board.pop()
                        
                        if is_safe:
                            if target_value > value:
                                score += (target_value - value) * 2  # Karlı ve güvenli değişim
                            else:
                                score += target_value  # Normal taş yeme
                        else:
                            if target_value > value:
                                score += target_value - value  # Riskli ama karlı değişim
                                
                    # Pozisyon iyileştirme
                    else:
                        # Merkez kontrolü
                        to_file = chess.square_file(move.to_square)
                        to_rank = chess.square_rank(move.to_square)
                        center_distance = abs(3.5 - to_file) + abs(3.5 - to_rank)
                        
                        if center_distance <= 2:  # Merkeze yakın hamle
                            score += (4 - center_distance) * 5
                            
                        # Açık hat kontrolü (kaleler için)
                        if piece.piece_type == chess.ROOK:
                            file_pawns = sum(1 for r in range(8)
                                          if board.piece_at(chess.square(to_file, r)) and
                                          board.piece_at(chess.square(to_file, r)).piece_type == chess.PAWN)
                            if file_pawns == 0:
                                score += 20
        
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Minimax algoritması ile en iyi hamleyi bul"""
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board), None
            
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                    
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_ai_move(self):
        """AI'nın hamlesini al"""
        # Oyun fazına göre derinliği ayarla
        total_pieces = len(self.board.piece_map())
        if total_pieces <= 10:  # Son oyun
            depth = 5
        elif total_pieces <= 20:  # Orta oyun
            depth = 4
        else:  # Açılış
            depth = 3
            
        _, best_move = self.minimax(self.board, depth, float('-inf'), float('inf'), True)
        return best_move

    def make_ai_move(self):
        """AI'nın hamle yapması"""
        if not self.board.is_game_over():
            best_move = self.get_ai_move()
            if best_move:
                # Piyon terfisi kontrolü
                if self.is_pawn_promotion(best_move):
                    # AI her zaman veziri seçer
                    best_move = chess.Move(
                        best_move.from_square,
                        best_move.to_square,
                        promotion=chess.QUEEN
                    )

                # Taşın alınıp alınmadığını kontrol et
                captured_piece = self.board.piece_at(best_move.to_square)
                
                # Hamleyi yap
                san_move = self.board.san(best_move)
                
                # Eğer bir taş alındıysa istatistiklere ekle
                if captured_piece:
                    piece_symbol = self.get_piece_unicode(captured_piece)
                    if self.board.turn:  # Beyaz hamle yapıyorsa (AI)
                        self.game_stats['white_captures'].append(piece_symbol)
                    else:  # Siyah hamle yapıyorsa (AI)
                        self.game_stats['black_captures'].append(piece_symbol)
                    self.update_capture_labels()

                self.board.push(best_move)
                
                # İstatistikleri güncelle
                self.game_stats['move_count'] += 1
                if self.board.is_check():
                    self.game_stats['check_count'] += 1
                    self.check_label.config(text="ŞAH!")
                else:
                    self.check_label.config(text="")
                
                # Hamle geçmişine ekle
                move_number = (len(self.move_history) // 2) + 1
                if len(self.move_history) % 2 == 0:
                    history_text = f"{move_number}. {san_move}"
                else:
                    history_text = f"    {san_move}"
                self.move_history.append(san_move)
                self.history_listbox.insert(tk.END, history_text)
                self.history_listbox.see(tk.END)
                
                # Tahtayı ve durumu güncelle
                self.update_board()
                self.update_status()
                self.update_game_status()

    def handle_pawn_promotion(self, move):
        """Piyon terfisi için kullanıcıdan seçim al"""
        promotion_window = tk.Toplevel(self.window)
        promotion_window.title("Piyon Terfisi")
        promotion_window.configure(bg="#2c3e50")
        
        # Pencereyi ana pencerenin ortasında göster
        window_width = 300
        window_height = 100
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        promotion_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Başlık
        tk.Label(
            promotion_window,
            text="Piyonunuzu terfi ettirin:",
            font=("Roboto", 14),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(pady=10)
        
        selected_piece = tk.StringVar(value="q")  # Varsayılan olarak vezir
        result = {'piece': None}
        
        def on_select(piece_type):
            result['piece'] = piece_type
            promotion_window.destroy()
        
        # Butonlar için frame
        button_frame = tk.Frame(promotion_window, bg="#2c3e50")
        button_frame.pack(fill="x", padx=20)
        
        # Terfi seçenekleri
        pieces = [
            ("♕ Vezir", "q"),
            ("♖ Kale", "r"),
            ("♗ Fil", "b"),
            ("♘ At", "n")
        ]
        
        for text, piece_type in pieces:
            tk.Button(
                button_frame,
                text=text,
                command=lambda p=piece_type: on_select(p),
                font=("Roboto", 12),
                bg="#ecf0f1",
                fg="#2c3e50",
                width=8
            ).pack(side="left", padx=5)
        
        # Pencere kapanana kadar bekle
        self.window.wait_window(promotion_window)
        
        if result['piece']:
            # Yeni hamle oluştur
            return chess.Move(
                move.from_square,
                move.to_square,
                promotion=chess.PIECE_SYMBOLS.index(result['piece'])
            )
        return None

    def is_pawn_promotion(self, move):
        """Hamlenin piyon terfisi olup olmadığını kontrol et"""
        piece = self.board.piece_at(move.from_square)
        if piece is None:
            return False
            
        # Piyon mu kontrol et
        if piece.piece_type != chess.PAWN:
            return False
            
        # Son sıraya ulaştı mı kontrol et
        rank = chess.square_rank(move.to_square)
        return (piece.color and rank == 7) or (not piece.color and rank == 0)

    def update_status(self):
        self.status_label.config(text="Siyah'ın hamlesi" if self.board.turn == chess.BLACK else "Beyaz'ın hamlesi")
    
    def update_game_status(self):
        """Oyun durumunu güncelle"""
        if self.board.is_game_over():
            self.handle_game_over(self.board.result())
        else:
            current_turn = "Beyaz" if self.board.turn else "Siyah"
            self.status_label.config(text=f"{current_turn}'ın hamlesi")
            
            if self.board.is_check():
                self.check_label.config(text="ŞAH!")
                self.game_stats['check_count'] += 1
            else:
                self.check_label.config(text="")

    def handle_game_over(self, result):
        """Oyun bittiğinde kullanıcıya seçenek sun"""
        message = ""
        if result == "1-0":
            message = "Beyaz kazandı!"
        elif result == "0-1":
            message = "Siyah kazandı!"
        else:
            message = "Berabere!"

        # Oyun sonu istatistiklerini ekle
        total_time = int(time.time() - self.game_stats['start_time'])
        stats = f"\n\nOyun İstatistikleri:\n"
        stats += f"Toplam Hamle: {self.game_stats['move_count']}\n"
        stats += f"Şah Durumu: {self.game_stats['check_count']} kez\n"
        stats += f"Oyun Süresi: {total_time} saniye"

        # Kullanıcıya sor
        answer = messagebox.askyesno(
            "Oyun Bitti",
            message + stats + "\n\nTekrar oynamak ister misiniz?"
        )
        
        # Her iki durumda da ana menüye dön
        self.show_main_menu()

    def update_capture_labels(self):
        """Alınan taşları gösteren etiketleri güncelle"""
        white_text = "Beyaz'ın aldığı taşlar: "
        black_text = "Siyah'ın aldığı taşlar: "
        
        # Beyazın aldığı taşları göster
        if self.game_stats['white_captures']:
            white_text += " ".join(self.game_stats['white_captures'])
        else:
            white_text += "Henüz taş alınmadı"
            
        # Siyahın aldığı taşları göster
        if self.game_stats['black_captures']:
            black_text += " ".join(self.game_stats['black_captures'])
        else:
            black_text += "Henüz taş alınmadı"
        
        self.white_captures_label.config(text=white_text)
        self.black_captures_label.config(text=black_text)

    def get_piece_unicode(self, piece):
        """Taş sembolünü Unicode karaktere çevir"""
        symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # Beyaz taşlar
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'   # Siyah taşlar
        }
        return symbols.get(piece.symbol(), '?')

    def setup_gui(self):
        """GUI bileşenlerini oluştur ve yerleştir"""
        # Ana container
        self.main_frame = tk.Frame(self.window, bg="#2c3e50")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Sol taraf - Satranç tahtası
        self.board_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.board_frame.pack(side="left", padx=(0, 20))

        # Sağ taraf - Hamle geçmişi ve durum
        self.right_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.right_frame.pack(side="left", fill="both", expand=True)

        # Durum etiketi
        self.status_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        self.status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Beyaz'ın hamlesi",
            font=("Helvetica", 14),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.status_label.pack(side="left")
        
        # Şah durumu etiketi
        self.check_label = tk.Label(
            self.status_frame,
            text="",
            font=("Helvetica", 14),
            bg="#2c3e50",
            fg="#e74c3c"
        )
        self.check_label.pack(side="right")

        # İstatistikler
        self.stats_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        self.stats_frame.pack(fill="x", pady=(0, 10))
        
        # Beyaz taşların aldıkları
        self.white_captures_label = tk.Label(
            self.stats_frame,
            text="Beyaz'ın aldığı taşlar:",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.white_captures_label.pack(anchor="w")
        
        # Siyah taşların aldıkları
        self.black_captures_label = tk.Label(
            self.stats_frame,
            text="Siyah'ın aldığı taşlar:",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.black_captures_label.pack(anchor="w")

        # Hamle geçmişi başlığı
        self.history_title = tk.Label(
            self.right_frame,
            text="Hamle Geçmişi",
            font=("Helvetica", 14, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.history_title.pack(pady=(0, 5))

        # Hamle geçmişi listesi
        self.history_frame = tk.Frame(
            self.right_frame,
            bg="#34495e",
            width=200,
            height=400
        )
        self.history_frame.pack(fill="both", expand=True)
        self.history_frame.pack_propagate(False)

        # Hamle geçmişi listbox
        self.history_listbox = tk.Listbox(
            self.history_frame,
            bg="#34495e",
            fg="#ecf0f1",
            font=("Helvetica", 12),
            selectmode="none",
            width=25
        )
        self.history_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Satranç tahtası kareleri
        self.squares = {}
        self.create_board()
    
    def create_board(self):
        # Satranç tahtası için frame
        board_container = tk.Frame(self.board_frame, bg="#2c3e50")
        board_container.pack(padx=10, pady=10)
        
        # Satranç tahtası ve koordinatlar için ana frame
        board_with_coords = tk.Frame(board_container, bg="#2c3e50")
        board_with_coords.pack(padx=10, pady=10)
        
        # Orta kısım (sol koordinatlar + tahta)
        middle_section = tk.Frame(board_with_coords, bg="#2c3e50")
        middle_section.pack()
        
        # Sol koordinatlar
        left_coords = tk.Frame(middle_section, bg="#2c3e50")
        left_coords.pack(side=tk.LEFT, padx=(0, 5))
        
        # Satranç tahtası
        board_section = tk.Frame(middle_section, bg="#2c3e50")
        board_section.pack(side=tk.LEFT)
        
        # Satranç tahtası frame'i
        self.frame = tk.Frame(board_section, bg="#2c3e50")
        self.frame.pack()
        
        # Alt koordinatlar için frame
        bottom_coords = tk.Frame(board_section, bg="#2c3e50")
        bottom_coords.pack(fill=tk.X)
        
        # Satranç tahtası düğmeleri
        self.buttons = []
        square_size = 60
        
        # Sol koordinatları yerleştir (8'den 1'e)
        for i in range(8):
            coord_frame = tk.Frame(left_coords, width=20, height=square_size, bg="#2c3e50")
            coord_frame.pack_propagate(False)
            coord_frame.pack()
            tk.Label(coord_frame, text=str(8-i), font=("Helvetica", 12), 
                    fg="#ecf0f1", bg="#2c3e50").place(relx=0.5, rely=0.5, anchor="center")
        
        # Satranç kareleri
        for row in range(8):
            button_row = []
            for col in range(8):
                # Her kare için bir frame
                square_frame = tk.Frame(
                    self.frame,
                    width=square_size,
                    height=square_size,
                    highlightthickness=0,
                    bg="#ecf0f1" if (row + col) % 2 == 0 else "#34495e"
                )
                square_frame.grid(row=row, column=col)
                square_frame.grid_propagate(False)
                
                # Her kare için bir label
                square_label = tk.Label(
                    square_frame,
                    width=square_size,
                    height=square_size,
                    bg="#ecf0f1" if (row + col) % 2 == 0 else "#34495e"
                )
                square_label.place(relx=0.5, rely=0.5, anchor="center")
                
                # Mouse olaylarını bağla
                square_label.bind("<Button-1>", lambda e, r=row, c=col: self.on_square_click(e, r, c))
                square_label.bind("<B1-Motion>", lambda e, r=row, c=col: self.on_square_drag(e, r, c))
                square_label.bind("<ButtonRelease-1>", lambda e, r=row, c=col: self.on_square_release(e, r, c))
                
                button_row.append(square_label)
            self.buttons.append(button_row)
        
        # Alt koordinatları yerleştir (A'dan H'ye)
        for i in range(8):
            coord_frame = tk.Frame(bottom_coords, width=square_size, height=20, bg="#2c3e50")
            coord_frame.pack_propagate(False)
            coord_frame.pack(side=tk.LEFT)
            tk.Label(coord_frame, text=chr(65+i), font=("Helvetica", 12),
                    fg="#ecf0f1", bg="#2c3e50").place(relx=0.5, rely=0.5, anchor="center")
        
        # İlk tahtayı çiz
        self.update_board()
    
    def show_main_menu(self):
        """Modern ana menüyü göster"""
        # Ana pencereyi yapılandır
        self.window.geometry("800x600")
        self.window.configure(bg="#2c3e50")

        # Ana penceredeki mevcut widget'ları temizle
        for widget in self.window.winfo_children():
            widget.destroy()

        # Ana menü frame'i
        menu_frame = tk.Frame(self.window, bg="#2c3e50")
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Başlık
        title = tk.Label(menu_frame, 
                        text="♔ Modern Satranç ♔",
                        font=("Helvetica", 36, "bold"),
                        bg="#2c3e50",
                        fg="#ecf0f1")
        title.pack(pady=30)

        # Alt başlık
        subtitle = tk.Label(menu_frame,
                          text="Zorluk Seviyesini Seçin",
                          font=("Helvetica", 18),
                          bg="#2c3e50",
                          fg="#bdc3c7")
        subtitle.pack(pady=(0, 30))

        # Zorluk seviyeleri için butonlar
        difficulties = [
            ("Kolay Seviye", "easy", "#27ae60"),
            ("Orta Seviye", "medium", "#2980b9"),
            ("Zor Seviye", "hard", "#c0392b")
        ]

        for text, value, color in difficulties:
            btn_frame = tk.Frame(menu_frame, bg="#2c3e50")
            btn_frame.pack(pady=10)
            
            btn = tk.Button(btn_frame, 
                          text=text,
                          font=("Helvetica", 14),
                          bg=color,
                          fg="#ffffff",
                          width=20,
                          height=2,
                          relief="flat",
                          command=lambda v=value: self.start_game(v))
            btn.pack()

            # Hover efekti
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=self.adjust_color(c, 1.1)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))

    def adjust_color(self, color, factor):
        """Rengi aydınlat/koyulaştır"""
        # Hex renk kodunu RGB'ye çevir
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Renkleri ayarla
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        # RGB'yi hex'e geri çevir
        return f"#{r:02x}{g:02x}{b:02x}"

    def start_game(self, difficulty):
        """Yeni oyun başlat"""
        self.difficulty = difficulty
        # Zorluk seviyesine göre AI'ı ayarla
        if difficulty == "easy":
            self.ai = ChessAI(difficulty="easy")
            difficulty_text = "Kolay Seviye"
        elif difficulty == "medium":
            self.ai = ChessAI(difficulty="medium")
            difficulty_text = "Orta Seviye"
        else:  # hard
            self.ai = AdvancedChessAI()
            difficulty_text = "Zor Seviye"

        # Oyunu sıfırla
        self.board = chess.Board()
        self.selected_square = None
        self.dragging = False
        self.drag_image_label = None
        self._current_drag_image = None
        self.possible_moves = []
        self.move_history = []
        self.game_stats = {
            'white_captures': [],
            'black_captures': [],
            'move_count': 0,
            'check_count': 0,
            'game_duration': 0,
            'start_time': time.time()
        }

        # Ana penceredeki menüyü temizle
        for widget in self.window.winfo_children():
            widget.destroy()

        # Oyun arayüzünü oluştur
        self.setup_gui()

        # Zorluk seviyesi göstergesi
        difficulty_label = tk.Label(
            self.right_frame,
            text=f"Zorluk: {difficulty_text}",
            font=("Helvetica", 12, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        difficulty_label.pack(pady=(0, 10))

        # Oyun tahtasını güncelle
        self.update_board()

    def reset_game(self):
        """Oyunu sıfırla ve yeni oyun başlat"""
        # Tahtayı sıfırla
        self.board = chess.Board()
        
        # İstatistikleri sıfırla
        self.game_stats = {
            'white_captures': [],
            'black_captures': [],
            'move_count': 0,
            'check_count': 0,
            'game_duration': 0,
            'start_time': time.time()
        }
        
        # Hamle geçmişini temizle
        self.move_history = []
        self.history_listbox.delete(0, tk.END)
        
        # Etiketleri sıfırla
        self.update_capture_labels()
        self.check_label.config(text="")
        
        # Seçimleri sıfırla
        self.selected_square = None
        self.dragging = False
        self.drag_image_label = None
        self._current_drag_image = None
        self.possible_moves = []
        
        # Tahtayı güncelle
        self.update_board()
        
        # Durumu güncelle
        self.status_label.config(text="Beyaz'ın hamlesi")

        # Ana menüye dön
        self.show_main_menu()

    def run(self):
        self.show_main_menu()
        self.window.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
