from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 主色 - 蓝色渐变背景
    primary_color = (37, 99, 235)  # #2563eb
    primary_dark = (30, 64, 175)   # #1e40af

    # 绘制圆角矩形背景
    margin = 20
    radius = 45
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=primary_color
    )

    # 绘制内部渐变效果（用半透明层模拟）
    inner_margin = 30
    draw.rounded_rectangle(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        radius=35,
        fill=(255, 255, 255, 30)
    )

    # 绘制转换箭头
    arrow_color = (255, 255, 255)
    center_x, center_y = size // 2, size // 2

    # 上箭头（代表图片）
    arrow_top = [
        (center_x - 50, center_y - 15),
        (center_x + 50, center_y - 15),
        (center_x + 50, center_y - 35),
        (center_x + 70, center_y - 10),
        (center_x + 50, center_y + 15),
        (center_x + 50, center_y - 5),
        (center_x - 50, center_y - 5),
    ]
    draw.polygon(arrow_top, fill=arrow_color)

    # 下箭头（代表转换后的格式）
    arrow_bottom = [
        (center_x - 50, center_y + 5),
        (center_x + 50, center_y + 5),
        (center_x + 50, center_y + 25),
        (center_x + 70, center_y),
        (center_x + 50, center_y - 25),
        (center_x + 50, center_y + 15),
        (center_x - 50, center_y + 15),
    ]
    draw.polygon(arrow_bottom, fill=(255, 255, 255, 180))

    # 绘制左右交换箭头
    left_x = center_x - 55
    right_x = center_x + 55

    # 左箭头（向内）
    draw.polygon([
        (left_x + 25, center_y - 20),
        (left_x + 5, center_y - 5),
        (left_x + 25, center_y + 10),
    ], fill=(255, 255, 255, 200))

    # 右箭头（向外）
    draw.polygon([
        (right_x - 25, center_y - 20),
        (right_x - 5, center_y - 5),
        (right_x - 25, center_y + 10),
    ], fill=(255, 255, 255, 200))

    return img

def create_icon_with_border():
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 外发光效果
    for i in range(3):
        offset = 15 - i * 3
        draw.rounded_rectangle(
            [offset, offset, size - offset, size - offset],
            radius=50 + i * 3,
            fill=(37, 99, 235, 30 + i * 20)
        )

    # 主背景
    draw.rounded_rectangle(
        [15, 15, size - 15, size - 15],
        radius=48,
        fill='#2563eb'
    )

    # 高光层
    draw.rounded_rectangle(
        [20, 20, size - 60, size - 80],
        radius=40,
        fill=(255, 255, 255, 40)
    )

    # 绘制简化的图片图标（上方）
    pic_margin = 60
    draw.rounded_rectangle(
        [pic_margin, pic_margin + 10, size - pic_margin, size // 2 + 10],
        radius=12,
        outline='white',
        width=3
    )

    # 绘制山形图案在图片内
    mountain_points = [
        (pic_margin + 20, size // 2 - 5),
        (pic_margin + 50, pic_margin + 30),
        (pic_margin + 80, size // 2 - 5),
    ]
    draw.polygon(mountain_points, fill=(255, 255, 255, 150))

    # 绘制太阳
    sun_x, sun_y = size - pic_margin - 30, pic_margin + 35
    draw.ellipse([sun_x - 10, sun_y - 10, sun_x + 10, sun_y + 10], fill='white')

    # 绘制转换箭头（中间）
    arr_center_y = size // 2 + 30
    arr_color = 'white'

    # 上箭头
    draw.polygon([
        (size // 2 - 20, arr_center_y - 25),
        (size // 2, arr_center_y - 40),
        (size // 2 + 20, arr_center_y - 25),
        (size // 2 + 20, arr_center_y - 10),
        (size // 2, arr_center_y - 20),
        (size // 2 - 20, arr_center_y - 10),
    ], fill=arr_color)

    # 下箭头
    draw.polygon([
        (size // 2 - 20, arr_center_y + 10),
        (size // 2, arr_center_y - 5),
        (size // 2 + 20, arr_center_y + 10),
        (size // 2 + 20, arr_center_y + 25),
        (size // 2, arr_center_y + 15),
        (size // 2 - 20, arr_center_y + 25),
    ], fill=(255, 255, 255, 180))

    # 绘制输出文件图标（下方）
    out_margin = 60
    file_top = size // 2 + 55
    draw.rounded_rectangle(
        [out_margin, file_top, size - out_margin, size - out_margin - 10],
        radius=12,
        outline='white',
        width=3
    )

    # 文件内的文字线条
    for i in range(3):
        line_y = file_top + 20 + i * 18
        line_width = 60 - i * 15
        draw.line([
            (out_margin + 20, line_y),
            (out_margin + 20 + line_width, line_y)
        ], fill=(255, 255, 255, 150), width=3)

    return img

# 生成图标
print("正在生成应用图标...")

# 创建大图标
icon = create_icon_with_border()
icon.save('app_icon.png', 'PNG')
print("已保存: app_icon.png")

# 创建多尺寸图标
sizes = [16, 32, 48, 64, 128, 256]
icons = []
for s in sizes:
    resized = icon.resize((s, s), Image.Resampling.LANCZOS)
    icons.append(resized)

# 保存为 ICO 文件
icon.save('app_icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
print("已保存: app_icon.ico")

# 生成半透明版本
icon_half = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
icon_half.paste(icon, (0, 0), mask=icon)
icon_half.save('app_icon_semi.png', 'PNG')
print("已保存: app_icon_semi.png")

print("\n图标生成完成！")
print("文件位置: " + os.path.abspath('app_icon.png'))
