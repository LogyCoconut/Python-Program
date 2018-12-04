from random import randrange, choice
from collections import defaultdict
import curses

# 用户行为,通过键入得到动作
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
letter_codes = ['W', 'A', 'S', 'D', 'R', 'Q', 'w', 'a', 's', 'd', 'r', 'q']
actions_dict = dict(zip(letter_codes, actions * 2))


def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]


# 转置矩阵
def transpose(field):
    return [list(row) for row in zip(*field)]


# 矩阵反转
def invert(field):
    return [row[::-1] for row in field]


class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.high_score = 0
        self.reset()

    def reset(self):
        """
        重置棋盘
        """
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        # 领域是一个二维数组
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        # 随机生成两个点
        self.spawn()
        self.spawn()

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                # 断言
                assert len(new_row) == len(row)
                return new_row

            return tighten(merge(tighten(row)))

        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def spawn(self):
        new_element = 4 if randrange(100) > 80 else 2
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def draw(self, screen):
        """
        绘制屏幕
        """
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            screen.addstr(string + '\n')

        # 水平线
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, "counter"):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1

        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        screen.clear()

        cast('SCORE:' + str(self.score))
        if 0 != self.high_score:
            cast('HIGHSCORE' + str(self.high_score))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False

            return any(change(i) for i in range(len(row) - 1))

        check = {}
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False


def main(stdscr):
    """
    主函数负责状态的切换
    """

    def init():
        # 重置游戏
        game_filed.reset()
        return 'Game'

    def game():
        # 同步棋盘状态 读取用户输入得到action
        game_filed.draw(stdscr)
        # 读取输入
        action = get_user_action(stdscr)

        if action == "Restart":
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_filed.move(action):
            if game_filed.is_win():
                return 'Win'
            if game_filed.is_gameover():
                return 'Gameover'
        return 'Game'

    def not_game(state):
        # 画出界面
        game_filed.draw(stdscr)
        # 读取输入
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]

    # 游戏可以 分成　初始化　游戏中　胜利或失败　退出五个状态
    state_actions = {
        'Init': init,
        'Game': game,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
    }

    curses.use_default_colors()

    game_filed = GameField()

    state = "Init"  # 初始状态

    while state != 'Exit':
        state = state_actions[state]()


curses.wrapper(main)