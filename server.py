import socket
import copy

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPServerSocket.bind(("127.0.0.1", 5000))

rooms = {}
players = {}
init_room = {
    "players": [],
    "moves": [],
    "board": [["x" for _ in range(15)] for _ in range(15)]
}


def add_move(room, color, x, y):
    room["board"][y][x] = color
    room["moves"].append((x, y))
    for player in room["players"]:
        UDPServerSocket.sendto(f'{color};{x};{y}'.encode(), player)


def send_result(result, room):
    player_black = room["players"][0]
    player_white = room["players"][1]

    if result == "b":
        UDPServerSocket.sendto("you_won;0;0".encode(), player_black)
        UDPServerSocket.sendto("you_lost;0;0".encode(), player_white)
    elif result == "w":
        UDPServerSocket.sendto("you_won;0;0".encode(), player_white)
        UDPServerSocket.sendto("you_lost;0;0".encode(), player_black)
    else:
        UDPServerSocket.sendto("tie;0;0".encode(), player_black)
        UDPServerSocket.sendto("tie;0;0".encode(), player_white)


while True:
    b, address = UDPServerSocket.recvfrom(1024)

    c, x, y = b.decode().split(";")

    if c == "join" and address not in players:
        if len(players) % 2 == 0:
            id = max(rooms, default=0) + 1
            players[address] = id
            rooms[id] = copy.deepcopy(init_room)
            rooms[id]["players"].append(address)
        else:
            id = max(rooms)
            players[address] = id
            rooms[id]["players"].append(address)

            if len(rooms[id]["moves"]) == 1:
                x, y = rooms[id]["moves"][0]
                UDPServerSocket.sendto(f'b;{x};{y}'.encode(), address)
    elif c == "move":
        x, y = int(x), int(y)
        id = players[address]
        room = rooms[id]

        # First move
        if len(room["moves"]) == 0:
            if x == 7 and y == 7:
                room["players"].remove(address)
                room["players"].insert(0, address)
                add_move(room, "b", x, y)
            else:
                UDPServerSocket.sendto("wrong_move;0;0".encode(), address)
        # Third move
        elif len(room["moves"]) == 2 and room["players"][0] == address and room["board"][y][x] == "x":
            if not (4 < x < 10 and 4 < y < 10):
                add_move(room, "b", x, y)
            else:
                UDPServerSocket.sendto("wrong_move;0;0".encode(), address)
        # White players move
        elif len(room["moves"]) % 2 != 0 and len(room["players"]) == 2 and room["players"][1] == address and room["board"][y][x] == "x":
            add_move(room, "w", x, y)
        # Black players move
        elif len(room["moves"]) % 2 == 0 and room["players"][0] == address and room["board"][y][x] == "x":
            add_move(room, "b", x, y)
        else:
            UDPServerSocket.sendto("wrong_move;0;0".encode(), address)

        board = room["board"]
        for i in range(15):
            for j in range(15):
                # Horizontal
                if j < 11 and "x" != board[i][j] == board[i][j + 1] == board[i][j + 2] == board[i][j + 3] == board[i][j + 4]:
                    send_result(board[i][j], room)
                # Vertical
                if i < 11 and "x" != board[i][j] == board[i + 1][j] == board[i + 2][j] == board[i + 3][j] == board[i + 4][j]:
                    send_result(board[i][j], room)
                # Diagonals
                if i < 11 and j < 11 and "x" != board[i][j] == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3] == board[i + 4][j + 4]:
                    send_result(board[i][j], room)
                if i > 3 and j < 11 and "x" != board[i][j] == board[i - 1][j + 1] == board[i - 2][j + 2] == board[i - 3][j + 3] == board[i - 4][j + 4]:
                    send_result(board[i][j], room)
        # Tie
        if len(room["moves"]) == 225:
            send_result("tie", room)

        rooms[id] = room
    elif c == "leave":
        if address in players:
            id = players[address]
            if id in rooms:
                for player in rooms[id]["players"]:
                    if player in players:
                        UDPServerSocket.sendto(f'leave;0;0'.encode(), player)
                        del players[player]
                del rooms[id]
