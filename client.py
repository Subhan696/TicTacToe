import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

class TicTacToeClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.symbol = ''
        self.running = True
        self.my_turn = False  # New flag to control input

    def connect(self):
        self.sock.connect((HOST, PORT))
        self.symbol = self.sock.recv(1024).decode()
        print(f"You are player {self.symbol}")
        threading.Thread(target=self.receive_updates).start()
        self.play()

    def print_board(self, board):
        print("\n---+---+---")
        for row in eval(board):
            print(f"{row[0]} | {row[1]} | {row[2]}")
            print("---+---+---")

    def receive_updates(self):
        while self.running:
            try:
                data = self.sock.recv(1024).decode()
                if data.startswith('Player'):
                    print(data)
                    self.running = False
                    break
                elif data == "Your turn":
                    self.my_turn = True  # Enable input
                    print("Your turn! Enter row and column (0-2).")
                elif data == "Invalid move":
                    print("Invalid move! Try again.")
                    self.my_turn = True  # Re-prompt
                else:
                    self.print_board(data)
            except:
                print("Disconnected from server.")
                self.sock.close()
                self.running = False
                break

    def play(self):
        while self.running:
            if self.my_turn:  # Only prompt when it's the player's turn
                try:
                    row = int(input("Enter row (0-2): "))
                    col = int(input("Enter column (0-2): "))
                    self.sock.sendall(f"{row},{col}".encode())
                    self.my_turn = False  # Disable input until next turn
                except:
                    print("Invalid input!")
                    self.my_turn = True  # Keep prompting on error

if __name__ == "__main__":
    client = TicTacToeClient()
    client.connect()