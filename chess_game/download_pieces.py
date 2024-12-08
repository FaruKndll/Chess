import os
import requests
from PIL import Image
from io import BytesIO

def download_pieces():
    # Create pieces directory if it doesn't exist
    pieces_dir = os.path.join(os.path.dirname(__file__), "pieces")
    os.makedirs(pieces_dir, exist_ok=True)
    
    # Chess piece URLs (PNG files)
    piece_urls = {
        'white_king': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wk.png',
        'white_queen': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wq.png',
        'white_bishop': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wb.png',
        'white_knight': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wn.png',
        'white_rook': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wr.png',
        'white_pawn': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wp.png',
        'black_king': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bk.png',
        'black_queen': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bq.png',
        'black_bishop': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bb.png',
        'black_knight': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bn.png',
        'black_rook': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/br.png',
        'black_pawn': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bp.png'
    }

    try:
        # Download each piece
        for piece_name, url in piece_urls.items():
            print(f"Downloading {piece_name}...")
            response = requests.get(url)
            if response.status_code == 200:
                # Convert to PNG and save
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGBA')
                img = img.resize((64, 64), Image.Resampling.LANCZOS)
                img.save(os.path.join(pieces_dir, f"{piece_name}.png"), 'PNG')
                print(f"Downloaded and saved {piece_name}")
            else:
                print(f"Failed to download {piece_name}")

        print("\nAll pieces downloaded successfully!")
        print("You can now run the chess game.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    download_pieces()
