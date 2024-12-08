import chess
import tkinter as tk
from tkinter import messagebox
import random
from piece_loader import PieceLoader

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Satranç Oyunu")
        self.board = chess.Board()
        self.selected_square = None
        self.pieces = PieceLoader(size=50)
        self.possible_moves = []
        self.move_history = []  # Hamle geçmişini tutacak liste
        self.setup_gui()
        
    def setup_gui(self):
        # Ana container
        main_container = tk.Frame(self.window)
        main_container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Sol panel (satranç tahtası)
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, padx=(0, 10))
        
        # Satranç tahtası için frame
        board_container = tk.Frame(left_panel)
        board_container.pack()
        
        # Satranç tahtası ve koordinatlar için ana frame
        board_with_coords = tk.Frame(board_container)
        board_with_coords.pack(padx=5, pady=5)
        
        # Orta kısım (sol koordinatlar + tahta)
        middle_section = tk.Frame(board_with_coords)
        middle_section.pack()
        
        # Sol koordinatlar
        left_coords = tk.Frame(middle_section)
        left_coords.pack(side=tk.LEFT, padx=(0, 5))
        
        # Satranç tahtası
        board_section = tk.Frame(middle_section)
        board_section.pack(side=tk.LEFT)
        
        # Satranç tahtası frame'i
        self.frame = tk.Frame(board_section)
        self.frame.pack()
        
        # Alt koordinatlar için frame
        bottom_coords = tk.Frame(board_section)
        bottom_coords.pack(fill=tk.X)
        
        # Satranç tahtası düğmeleri
        self.buttons = []  # İlk önce boş liste olarak başlat
        square_size = 60
        
        # Sol koordinatları yerleştir (8'den 1'e)
        for i in range(8):
            coord_frame = tk.Frame(left_coords, width=20, height=square_size)
            coord_frame.pack_propagate(False)
            coord_frame.pack()
            tk.Label(coord_frame, text=str(8-i), font=('Arial', 12)).place(relx=0.5, rely=0.5, anchor="center")
        
        # Satranç kareleri
        for row in range(8):
            button_row = []  # Her satır için yeni bir liste
            for col in range(8):
                # Her kare için bir frame oluştur
                square_frame = tk.Frame(
                    self.frame,
                    width=square_size,
                    height=square_size,
                    bg="#ffffff" if (row + col) % 2 == 0 else "#4b7399"
                )
                square_frame.grid(row=row, column=col)
                square_frame.grid_propagate(False)
                
                # Düğmeyi frame içine yerleştir
                button = tk.Button(
                    square_frame,
                    bg="#ffffff" if (row + col) % 2 == 0 else "#4b7399",
                    bd=0,
                    highlightthickness=0,
                    command=lambda r=row, c=col: self.square_clicked(r, c)
                )
                button.place(relx=0.5, rely=0.5, anchor="center")
                button_row.append(button)  # Butonu satıra ekle
            self.buttons.append(button_row)  # Satırı buttons listesine ekle
        
        # Alt koordinatları yerleştir (A'dan H'ye)
        for i in range(8):
            coord_frame = tk.Frame(bottom_coords, width=square_size, height=20)
            coord_frame.pack_propagate(False)
            coord_frame.pack(side=tk.LEFT)
            tk.Label(coord_frame, text=chr(65+i), font=('Arial', 12)).place(relx=0.5, rely=0.5, anchor="center")
        
        # Sağ panel (bilgi paneli)
        info_panel = tk.Frame(main_container)
        info_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Durum etiketi
        self.status_label = tk.Label(info_panel, text="Beyaz'ın hamlesi", font=('Arial', 12))
        self.status_label.pack(pady=(0, 10))
        
        # Şah durumu etiketi
        self.check_label = tk.Label(info_panel, text="", fg="red", font=('Arial', 12))
        self.check_label.pack(pady=(0, 10))
        
        # Hamle geçmişi başlığı
        history_title = tk.Label(info_panel, text="Hamle Geçmişi", font=('Arial', 12, 'bold'))
        history_title.pack(pady=(0, 5))
        
        # Hamle geçmişi text widget'ı
        self.move_history_text = tk.Text(info_panel, height=20, width=20, font=('Arial', 10))
        self.move_history_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_board()
        
    def get_piece_symbol(self, piece):
        if piece is None:
            return None
            
        color = 'w' if piece.color == chess.WHITE else 'b'
        piece_type = piece.symbol().lower()
        return f"{color}{piece_type}"
        
    def update_board(self):
        if not hasattr(self, 'buttons') or not self.buttons:
            return
            
        for row in range(8):
            for col in range(8):
                # Tahtayı ters çevir: 7-row kullanarak alt taraftan başla
                square = (7-row) * 8 + col
                piece = self.board.piece_at(square)
                button = self.buttons[row][col]
                
                if button is None:
                    continue
                    
                frame = button.master
                if frame is None:
                    continue
                
                # Temel arka plan rengini ayarla
                base_color = "#ffffff" if (row + col) % 2 == 0 else "#4b7399"
                if hasattr(button, 'config'):
                    button.config(bg=base_color)
                if hasattr(frame, 'config'):
                    frame.config(bg=base_color)
                
                # Seçili kare için ince kenarlık
                if square == self.selected_square and hasattr(button, 'config'):
                    button.config(highlightbackground="#90EE90", highlightthickness=2)
                # Olası hamleler için gösterge
                elif square in [move.to_square for move in self.possible_moves]:
                    if self.board.piece_at(square) and hasattr(button, 'config'):  # Rakip taş varsa
                        button.config(bg="#ff9999")  # Kırmızı arka plan
                    else:
                        # Boş kare için küçük bir daire göstergesi
                        if hasattr(button, 'winfo_children'):
                            for widget in button.winfo_children():
                                if isinstance(widget, tk.Canvas):
                                    widget.destroy()
                        
                        indicator = tk.Canvas(button, width=10, height=10, bg=base_color, highlightthickness=0)
                        indicator.create_oval(2, 2, 8, 8, fill="#90caf9", outline="")
                        indicator.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    if hasattr(button, 'config'):
                        button.config(highlightthickness=0)
                    # Eski göstergeleri temizle
                    if hasattr(button, 'winfo_children'):
                        for widget in button.winfo_children():
                            if isinstance(widget, tk.Canvas):
                                widget.destroy()
                
                # Taş görüntüsünü ayarla
                piece_symbol = self.get_piece_symbol(piece)
                if piece_symbol and hasattr(button, 'config'):
                    piece_image = self.pieces.get_piece_image(piece_symbol)
                    if piece_image:
                        button.config(image=piece_image, width=50, height=50)
                        button.image = piece_image  # Referansı sakla
                elif hasattr(button, 'config'):
                    button.config(image="", width=4, height=2)
                    
    def square_clicked(self, row, col):
        # Tahtayı ters çevir: 7-row kullanarak alt taraftan başla
        square = (7-row) * 8 + col
        
        if self.selected_square is None:
            # Taş seçme
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:  # Sadece beyaz taşları seçebilir
                self.selected_square = square
                # Olası hamleleri hesapla
                self.possible_moves = [move for move in self.board.legal_moves 
                                    if move.from_square == square]
        else:
            # Hamle yapma
            move = chess.Move(self.selected_square, square)
            
            # Piyon terfisi kontrolü
            if self.is_pawn_promotion(move):
                move = self.handle_pawn_promotion(move)
            
            if move in self.board.legal_moves:
                self.make_move(move)
                # AI hamlesi
                self.make_ai_move()
            
            # Seçimi ve olası hamleleri temizle
            self.clear_selection()
            
        self.update_board()
        self.check_game_state()
    
    def clear_selection(self):
        self.selected_square = None
        self.possible_moves = []
    
    def is_pawn_promotion(self, move):
        piece = self.board.piece_at(move.from_square)
        return (piece is not None and piece.piece_type == chess.PAWN and 
                ((move.to_square < 8 and piece.color == chess.BLACK) or
                 (move.to_square >= 56 and piece.color == chess.WHITE)))
    
    def handle_pawn_promotion(self, move):
        promotion_window = tk.Toplevel(self.window)
        promotion_window.title("Piyon Terfisi")
        promotion_window.grab_set()
        
        promotion_piece = None
        
        def set_promotion(piece_type):
            nonlocal promotion_piece
            promotion_piece = piece_type
            promotion_window.destroy()
        
        pieces = [
            ("Vezir", chess.QUEEN),
            ("Kale", chess.ROOK),
            ("Fil", chess.BISHOP),
            ("At", chess.KNIGHT)
        ]
        
        for piece_name, piece_type in pieces:
            tk.Button(promotion_window, text=piece_name,
                     command=lambda pt=piece_type: set_promotion(pt)).pack()
        
        self.window.wait_window(promotion_window)
        
        return chess.Move(move.from_square, move.to_square, promotion=promotion_piece)
    
    def square_to_coords(self, square):
        """Kare numarasını satranç koordinatlarına çevirir (örn: 0 -> a8)"""
        file_letter = chr(ord('a') + (square % 8))
        rank_number = 8 - (square // 8)  # 8'den başlayıp aşağı doğru giden koordinat
        return f"{file_letter}{rank_number}"

    def make_move(self, move):
        # Hamleyi yap ve SAN notasyonunu al
        san_move = self.board.san(move)
        self.board.push(move)
        
        # Hamle geçmişini güncelle
        self.move_history.append(san_move)
        self.update_move_history()
        
        # Şah kontrolü
        if self.board.is_check():
            self.check_label.config(text="ŞAH!")
        else:
            self.check_label.config(text="")
        
        # Durum etiketini güncelle
        self.status_label.config(text="Siyah'ın hamlesi" if self.board.turn == chess.BLACK else "Beyaz'ın hamlesi")

    def make_ai_move(self):
        if not self.board.is_game_over():
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                # Rastgele hamle seç
                ai_move = random.choice(legal_moves)
                
                # Hamleyi yap ve SAN notasyonunu al
                san_move = self.board.san(ai_move)
                self.board.push(ai_move)
                
                # Hamle geçmişini güncelle
                self.move_history.append(san_move)
                self.update_move_history()
                
                # Şah kontrolü
                if self.board.is_check():
                    self.check_label.config(text="ŞAH!")
                else:
                    self.check_label.config(text="")
                
                # Durum etiketini güncelle
                self.status_label.config(text="Beyaz'ın hamlesi")

    def update_move_history(self):
        self.move_history_text.delete('1.0', tk.END)
        for i in range(0, len(self.move_history), 2):
            move_number = i // 2 + 1
            white_move = self.move_history[i] if i < len(self.move_history) else ""
            black_move = self.move_history[i + 1] if i + 1 < len(self.move_history) else ""
            
            # Her hamle çifti için bir satır oluştur
            line = f"{move_number}. {white_move:<15} {black_move}\n"
            self.move_history_text.insert(tk.END, line)
    
    def check_game_state(self):
        if self.board.is_game_over():
            result = "1-0" if self.board.is_checkmate() and not self.board.turn else "0-1"
            message = "Oyun bitti! "
            if self.board.is_checkmate():
                message += "Şah mat! " + ("Siyah" if self.board.turn else "Beyaz") + " kazandı!"
            elif self.board.is_stalemate():
                message += "Pat! Berabere!"
            elif self.board.is_insufficient_material():
                message += "Yetersiz materyal! Berabere!"
            messagebox.showinfo("Oyun Bitti", message)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
