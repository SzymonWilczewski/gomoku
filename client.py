import pygame
import socket
import signal
import select

BOARD = (255, 200, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Gomoku:
    def __init__(self):
        self.x, self.y = None, None
        self.wh = 720
        self.title = "Gomoku"
        self.screen = pygame.display.set_mode((self.wh + 48, self.wh + 48))
        pygame.display.set_caption(self.title)
        self.screen.fill(BOARD)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.message_blit = ()
        self.message_end = 0

    def draw_board(self):
        for i in range(1, 16):
            pygame.draw.line(self.screen, BLACK, [48 * i, 48], [48 * i, self.wh], 2)
            pygame.draw.line(self.screen, BLACK, [48, 48 * i], [self.wh, 48 * i], 2)

        pygame.draw.circle(self.screen, BLACK, [48 * 8 + 1, 48 * 8 + 1], 8)

        pygame.draw.circle(self.screen, BLACK, [48 * 4 + 1, 48 * 4 + 1], 4)
        pygame.draw.circle(self.screen, BLACK, [48 * 4 + 1, 48 * 12 + 1], 4)
        pygame.draw.circle(self.screen, BLACK, [48 * 12 + 1, 48 * 4 + 1], 4)
        pygame.draw.circle(self.screen, BLACK, [48 * 12 + 1, 48 * 12 + 1], 4)

        pygame.draw.rect(self.screen, BLACK, pygame.Rect(48 * 6, 48 * 6, 48 * 4 + 2, 48 * 4 + 2), 3)

    def get_move(self):
        self.x, self.y = pygame.mouse.get_pos()

        self.x = (self.x - 24) // 48
        self.y = (self.y - 24) // 48

        if self.x < 0:
            self.x = 0
        if self.x > 14:
            self.x = 14
        if self.y < 0:
            self.y = 0
        if self.y > 14:
            self.y = 14

        return self.x, self.y

    def message(self, message, milliseconds=2000):
        text = self.font.render(message, True, BLACK, BOARD)
        text_rect = text.get_rect()
        text_rect.center = ((self.wh + 48) // 2, 26)
        self.message_blit = (text, text_rect)
        self.message_end = pygame.time.get_ticks() + milliseconds

    def no_message(self):
        pygame.draw.rect(self.screen, BOARD, pygame.Rect(0, 0, self.wh + 48, 48))

    def draw_stone(self, color, x, y):
        pygame.draw.circle(self.screen, color, [x * 48 + 49, y * 48 + 49], 22)


UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('127.0.0.1', 5000)


def stop_server(signum, frame):
    UDPClientSocket.sendto('leave;0;0'.encode(), address)
    exit()


signal.signal(signal.SIGINT, stop_server)
signal.signal(signal.SIGTERM, stop_server)

if __name__ == '__main__':
    pygame.init()
    game = Gomoku()
    game.draw_board()
    UDPClientSocket.sendto('join;0;0'.encode(), address)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = game.get_move()
                UDPClientSocket.sendto(f'move;{x};{y}'.encode(), address)

        if select.select([UDPClientSocket], [], [], 0)[0]:
            b, address = UDPClientSocket.recvfrom(1024)
            c, x, y = b.decode().split(";")
            x, y = int(x), int(y)

            if c == "b":
                game.draw_stone(BLACK, x, y)
            elif c == "w":
                game.draw_stone(WHITE, x, y)
            elif c == "wrong_move":
                game.message("WRONG MOVE")
            elif c == "you_won":
                game.message("YOU WON", 60000)
                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
            elif c == "you_lost":
                game.message("YOU LOST", 60000)
                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
            elif c == "tie":
                game.message("TIE", 60000)
                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
            elif c == "leave":
                running = False

        if game.message_blit and pygame.time.get_ticks() < game.message_end:
            game.screen.blit(*game.message_blit)
        else:
            game.no_message()

        pygame.display.update()

UDPClientSocket.sendto('leave;0;0'.encode(), address)
pygame.quit()
