import os
from PIL import Image, ImageTk

class PieceLoader:
    def __init__(self, size=64):
        self.piece_size = size
        self.pieces = {}
        self.piece_path = os.path.join(os.path.dirname(__file__), "pieces")
        self.load_pieces()

    def load_pieces(self):
        # White pieces file names
        white_pieces = {
            'wp': 'white_pawn',
            'wr': 'white_rook',
            'wn': 'white_knight',
            'wb': 'white_bishop',
            'wq': 'white_queen',
            'wk': 'white_king'
        }

        # Black pieces file names
        black_pieces = {
            'bp': 'black_pawn',
            'br': 'black_rook',
            'bn': 'black_knight',
            'bb': 'black_bishop',
            'bq': 'black_queen',
            'bk': 'black_king'
        }

        # Load white pieces
        for piece_code, piece_name in white_pieces.items():
            image_path = os.path.join(self.piece_path, f"{piece_name}.png")
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((self.piece_size, self.piece_size), Image.Resampling.LANCZOS)
                self.pieces[piece_code] = ImageTk.PhotoImage(img)
            else:
                print(f"File not found: {image_path}")

        # Load black pieces
        for piece_code, piece_name in black_pieces.items():
            image_path = os.path.join(self.piece_path, f"{piece_name}.png")
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((self.piece_size, self.piece_size), Image.Resampling.LANCZOS)
                self.pieces[piece_code] = ImageTk.PhotoImage(img)
            else:
                print(f"File not found: {image_path}")

    def get_piece_image(self, piece_code):
        return self.pieces.get(piece_code)
