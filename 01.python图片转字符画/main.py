from PIL import Image
import argparse

# 添加参数, 可指定输出方式以及长宽
parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('-o', '--output')
parser.add_argument('--width', type=int, default=80)
parser.add_argument('--height', type=int, default=40)

# 获取参数
args = parser.parse_args()
IMG = args.file
WIDTH = args.width
HEIGHT = args.height
OUTPUT = args.output

# 建立字符列表,
ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")


# 将256灰度映射到字符列表上, alpha代表透明度
def get_char(r, g, b, alpha=256):
    # 如果透明，返回一个空格
    if alpha == 0:
        return ' '

    length = len(ascii_char)
    # 灰度转换公式（不唯一）
    gray = int(0.2126*r + 0.7152*g + 0.0722*b)

    # 将灰度按比例映射到字符列表中
    return ascii_char[int(gray/256*length)]


if __name__ == '__main__':
    im = Image.open(IMG)
    im = im.resize((WIDTH, HEIGHT), Image.ANTIALIAS)  # 第二个参数指定质量，ANTIALIAS表示高质量，NEAREST表示低质量

    txt = ""

    # 从左到右,从顶向下
    for i in range(HEIGHT):
        for j in range(WIDTH):
            txt += get_char(*im.getpixel((j, i)))  # getpixel获取当前位置像素点的值，而加*表示以元组方式传递
        txt += "\n"

    # 打印结果
    print(txt)

    # 输出到文件
    if not OUTPUT:
        OUTPUT = "output.txt"

    with open(OUTPUT, "w") as f:
        f.write(txt)
