from random import randrange, choice
from collections import defaultdict
import curses

# 绑定码值与动作
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']  # 将返回字符所对应的ASCII码值
actions_dict = dict(zip(letter_codes, actions*2))


# 获取用户输入
def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]


# 转置矩阵
def transpose(field):
    return [list(row) for row in zip(*field)]  # zip将field组合，再将他们组成列表


# 矩阵逆转
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

    def spawn(self):
        """
        在数字为0(既空)的位置随机生成一个点
        """
        new_element = 4 if randrange(100)>80 else 2
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j]==0])
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

        # 包裹矩阵的水平线
        def draw_hor_separator():
            cast('+------' * self.width + '+')

        # 每一行
        def draw_row(row):
            # format是格式化函数，类似%d，但是功能更加强大
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')  # {:^5} ^表示居中对齐，宽度为５

        screen.clear()

        # 投射当前分数与最高分
        cast('SCORE:' + str(self.score))
        if 0 != self.high_score:
            cast('HIGHSCORE' + str(self.high_score))

        # 画矩阵
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

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row)-len(new_row))]
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2*row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i+1 < len(row) and row[i] == row[i+1]:
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
            # 成功的移动后才返回True
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row)-1))

        check = {}
        check['Left'] = lambda field:any(row_is_left_movable(row) for row in field)
        check['Right'] = lambda field:check['Left'](invert(field))
        check['Up'] = lambda field:check['Left'](transpose(field))
        check['Down'] = lambda field:check['Right'](transpose(field))


        if direction in check:
            return check[direction](self.field)
        else:
            return False


def main(stdscr):
    """
    主函数，状态转换函数
    stdscr: stdscr是一块逻辑屏幕，在curses函数库产生输出时就刷新
    """
    def init():
        # 重置游戏
        game_field.reset()
        return 'Game'

    def game():
        # 同步棋盘状态 读取用户输入得到action
        game_field.draw(stdscr)
        # 读取输入
        action = get_user_action(stdscr)

        if action == "Restart":
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    def not_game(state):
        # 画出界面, 读取输入
        game_field.draw(stdscr)
        action = get_user_action(stdscr)

        # 在赢或者输的情况下,除了初始化或者退出之外的操作都应该屏蔽,所以在字典中只添加两个键，其余的action只会保持原来的状态
        # defaultdict接受一个函数参数，默认值就是函数的默认值
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

    game_field = GameField(win=64)

    state = "Init"  # 初始状态

    while state != 'Exit':
        state = state_actions[state]()


curses.wrapper(main)
