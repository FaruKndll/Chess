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
        self.pieces = PieceLoader(size=50)  # Taş boyutunu küçülttük
        self.possible_moves = []
        self.setup_gui()
        
    def setup_gui(self):
        # Ana çerçeve
        self.frame = tk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)
        
        # Satranç tahtası düğmeleri
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        
        # Karelerin boyutunu ayarla
        square_size = 60
        
        for row in range(8):
            for col in range(8):
                # Her kare için bir frame oluştur
                square_frame = tk.Frame(
                    self.frame,
                    width=square_size,
                    height=square_size,
                    bg="#ffffff" if (row + col) % 2 == 0 else "#4b7399"
                )
                square_frame.grid(row=row, column=col)
                square_frame.grid_propagate(False)  # Frame boyutunu sabitle
                
                # Düğmeyi frame içine yerleştir
                button = tk.Button(
                    square_frame,
                    bg="#ffffff" if (row + col) % 2 == 0 else "#4b7399",
                    bd=0,  # Kenarlığı kaldır
                    highlightthickness=0,  # Vurgu kenarlığını kaldır
                    command=lambda r=row, c=col: self.square_clicked(r, c)
                )
                button.place(relx=0.5, rely=0.5, anchor="center")  # Düğmeyi ortala
                self.buttons[row][col] = button
        
        # Durum etiketi
        self.status_label = tk.Label(self.window, text="Beyaz'ın hamlesi")
        self.status_label.pack(pady=5)
        
        self.update_board()
        
    def get_piece_symbol(self, piece):
        if piece is None:
            return None
            
        color = 'w' if piece.color == chess.WHITE else 'b'
        piece_type = piece.symbol().lower()
        return f"{color}{piece_type}"
        
    def update_board(self):
        for row in range(8):
            for col in range(8):
                square = row * 8 + col
                piece = self.board.piece_at(square)
                button = self.buttons[row][col]
                frame = button.master
                
                # Arka plan rengini ayarla
                base_color = "#ffffff" if (row + col) % 2 == 0 else "#4b7399"
                color = base_color
                
                # Seçili kare için renk
                if square == self.selected_square:
                    color = "#90EE90"  # Açık yeşil
                # Olası hamleler için renk
                elif square in [move.to_square for move in self.possible_moves]:
                    if self.board.piece_at(square):  # Rakip taş varsa
                        color = "#ff9999"  # Kırmızımsı
                    else:
                        color = "#90caf9"  # Açık mavi
                
                button.config(bg=color)
                frame.config(bg=color)
                
                # Taş görüntüsünü ayarla
                piece_symbol = self.get_piece_symbol(piece)
                if piece_symbol:
                    piece_image = self.pieces.get_piece_image(piece_symbol)
                    if piece_image:
                        button.config(image=piece_image, width=50, height=50)
                        button.image = piece_image
                else:
                    button.config(image="", width=4, height=2)
                    
    def square_clicked(self, row, col):
        square = row * 8 + col
        
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
    
    def make_move(self, move):
        san_move = self.board.san(move)
        self.board.push(move)
        
        # Şah kontrolü
        if self.board.is_check():
            messagebox.showinfo("Şah!", "Şah çekildi!")
        
        # Durum etiketini güncelle
        self.status_label.config(text="Siyah'ın hamlesi" if self.board.turn == chess.BLACK else "Beyaz'ın hamlesi")
    
    def make_ai_move(self):
        if not self.board.is_game_over():
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                # Basit AI: rastgele hamle yap
                ai_move = random.choice(legal_moves)
                san_move = self.board.san(ai_move)
                self.board.push(ai_move)
                
                # Şah kontrolü
                if self.board.is_check():
                    messagebox.showinfo("Şah!", "Şah çekildi!")
                
                # Durum etiketini güncelle
                self.status_label.config(text="Beyaz'ın hamlesi")
    
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
