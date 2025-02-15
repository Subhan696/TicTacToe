import socket
import threading

# Server configuration
HOST = '127.0.0.1'
PORT = 65432

class TicTacToeServer:
    def __init__(self):
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.players = []
        self.symbols = ['X', 'O']
        self.current_turn = 0
        self.lock = threading.Lock()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(2)
            print("Server is listening for connections...")
            for _ in range(2):
                conn, addr = s.accept()
                print(f"Connected to {addr}")
                self.players.append(conn)
                # Send symbol to player
                conn.sendall(self.symbols[len(self.players)-1].encode())
            # Start game thread
            threading.Thread(target=self.game_loop).start()

    def send_board(self):
        board_str = str(self.board)
        for player in self.players:
            player.sendall(board_str.encode())

    def game_loop(self):
        self.send_board()
        while True:
            current_player = self.players[self.current_turn]
            current_player.sendall("Your turn".encode())
            # Receive move
            try:
                data = current_player.recv(1024).decode()
                row, col = map(int, data.split(','))
            except:
                print("Player disconnected")
                self.handle_disconnect()
                break
            # Validate move
            if self.board[row][col] != " ":
                current_player.sendall("Invalid move".encode())
                continue
            # Update board
            with self.lock:
                self.board[row][col] = self.symbols[self.current_turn]
                # Check winner
                if self.check_winner():
                    self.send_result(f"Player {self.symbols[self.current_turn]} wins!")
                    break
                if self.is_draw():
                    self.send_result("It's a draw!")
                    break
                # Switch turn
                self.current_turn = 1 - self.current_turn
                self.send_board()

    def check_winner(self):
        # Check rows, columns, diagonals
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True
        return False

    def is_draw(self):
        for row in self.board:
            if " " in row:
                return False
        return True

    def send_result(self, result):
        for player in self.players:
            player.sendall(result.encode())
        self.reset()

    def handle_disconnect(self):
        for player in self.players:
            player.sendall("Opponent disconnected".encode())
        self.reset()

    def reset(self):
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        for player in self.players:
            player.close()
        self.players = []

if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()