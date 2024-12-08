from PIL import Image, ImageTk
import os

class ChessPieces:
    def __init__(self):
        self.pieces = {}
        self.piece_size = 50
        self.load_pieces()

    def load_pieces(self):
        piece_types = ['p', 'r', 'n', 'b', 'q', 'k']
        colors = ['w', 'b']
        piece_folder = "C:/Users/Huawei/Desktop/chess_pieces"
        
        for color in colors:
            for piece in piece_types:
                piece_name = f"{color}{piece}"
                # Dosya adını düzelt (örn: wp.png, bk.png gibi)
                image_path = os.path.join(piece_folder, f"{piece_name}.png")
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((self.piece_size, self.piece_size), Image.Resampling.LANCZOS)
                    self.pieces[piece_name] = ImageTk.PhotoImage(img)

    def get_piece_image(self, piece_name):
        return self.pieces.get(piece_name)
