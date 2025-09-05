# from PIL import Image, ImageDraw, ImageFont

# ROWS, COLS = 28, 25
# GRID_LINE_WIDTH = 0.5  # now used for dotted lines
# BOLD_LINE_WIDTH = 1
# OUTER_PADDING = 25
# CELL_PADDING = 2
# FONT_PATH = "/home/evid/ABDUMAJID/CODING/PROJECTS/topik_essay/utils/NotoSans.ttf"

# def draw_dotted_line(draw, start, end, spacing=4, width=0.5, fill="black"):
#     """Draw a dotted line between start and end coordinates."""
#     x0, y0 = start
#     x1, y1 = end
#     if x0 == x1:  # vertical
#         y = y0
#         while y < y1:
#             y_end = min(y + spacing/2, y1)
#             draw.line([(x0, y), (x0, y_end)], fill=fill, width=width)
#             y += spacing
#     elif y0 == y1:  # horizontal
#         x = x0
#         while x < x1:
#             x_end = min(x + spacing/2, x1)
#             draw.line([(x, y0), (x_end, y0)], fill=fill, width=width)
#             x += spacing

# def create_grid_image(text: str, rows=ROWS, cols=COLS, highlight_positions=None):
#     highlight_positions = set(highlight_positions or [])

#     max_cell_w, max_cell_h = 28, 28
#     font_size = max_cell_h - CELL_PADDING * 5
#     try:
#         font = ImageFont.truetype(FONT_PATH, font_size)
#         font_small = ImageFont.truetype(FONT_PATH, 15)
#         font_punc = ImageFont.truetype(FONT_PATH, int(font_size * 0.8))
#     except:
#         font = ImageFont.load_default()
#         font_small = ImageFont.load_default()
#         font_punc = ImageFont.load_default()

#     cell_w, cell_h = max_cell_w, max_cell_h
#     grid_w, grid_h = cols * cell_w, rows * cell_h
#     img_w = grid_w + OUTER_PADDING * 2 + 40
#     img_h = grid_h + OUTER_PADDING * 2 + 80

#     img = Image.new("RGB", (img_w, img_h), "white")
#     draw = ImageDraw.Draw(img)

#     # HEADER
#     draw.text((OUTER_PADDING, 10), "54 - Essay Sheet", fill="black", font=font_small)
#     draw.text((img_w - OUTER_PADDING - 260, 10), "Name: ____________________", fill="black", font=font_small)

#     top_y = OUTER_PADDING + 20
#     left_x = OUTER_PADDING

#     # HORIZONTAL LINES
#     for r in range(rows + 1):
#         y = top_y + r * cell_h
#         width = BOLD_LINE_WIDTH if r % 4 == 0 else GRID_LINE_WIDTH
#         if r % 4 == 0:
#             draw.line([(left_x, y), (left_x + grid_w, y)], fill="black", width=int(width))
#         else:
#             draw_dotted_line(draw, (left_x, y), (left_x + grid_w, y), spacing=6, width=1)

#     # VERTICAL LINES
#     for c in range(cols + 1):
#         x = left_x + c * cell_w
#         width = BOLD_LINE_WIDTH if c % 5 == 0 else GRID_LINE_WIDTH
#         if c % 5 == 0:
#             draw.line([(x, top_y), (x, top_y + grid_h)], fill="black", width=int(width))
#         else:
#             draw_dotted_line(draw, (x, top_y), (x, top_y + grid_h), spacing=6, width=1)

#     # ROW NUMBERS
#     for r in range(2, rows + 1, 2):
#         number = 50 * (r // 2)
#         y = top_y + r * cell_h - cell_h // 3 - 5
#         draw.text((left_x + grid_w + 5, y), str(number), fill="black", font=font_small)

#     # TEXT IN CELLS
#     for idx, ch in enumerate(text):
#         row, col = divmod(idx, cols)
#         if row >= rows:
#             break
#         x0 = left_x + col * cell_w
#         y0 = top_y + row * cell_h
#         fnt = font_punc if ch in ".,!?;:()[]{}\"'" else font
#         bbox = draw.textbbox((0, 0), ch, font=fnt)
#         w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
#         x = x0 + (cell_w - w) / 2
#         y = y0 + (cell_h - h) / 2
#         color = "red" if (row, col) in highlight_positions else "black"
#         draw.text((x, y), ch, font=fnt, fill=color)

#     # FOOTER
#     footer_en = "Please don't turn answer sheet horizontally, or else you will get 100 points."
#     footer_kr = "답안지를 가로로 돌리지 마세요, 그렇지 않으면 100점을 받습니다."
#     draw.text((OUTER_PADDING, img_h - 80), footer_en, fill="black", font=font_small)
#     draw.text((OUTER_PADDING, img_h - 50), footer_kr, fill="black", font=font_small)

#     return img


from PIL import Image, ImageDraw, ImageFont

ROWS, COLS = 28, 25
GRID_LINE_WIDTH = 1        # thin, subtle lines
BOLD_LINE_WIDTH = 1        # slightly bolder lines
OUTER_PADDING = 25
CELL_PADDING = 2
FONT_PATH = "/home/evid/ABDUMAJID/CODING/PROJECTS/topik_essay/utils/NotoSans.ttf"

def draw_dotted_line(draw, start, end, spacing=6, width=1, fill=(0,0,0,100)):
    x1, y1 = start
    x2, y2 = end
    total_len = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    dx = (x2 - x1) / total_len
    dy = (y2 - y1) / total_len
    steps = int(total_len // spacing)
    for i in range(steps):
        sx = x1 + dx * spacing * i
        sy = y1 + dy * spacing * i
        ex = x1 + dx * spacing * (i + 0.5)
        ey = y1 + dy * spacing * (i + 0.5)
        draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)

def create_grid_image(text: str, rows=ROWS, cols=COLS, highlight_positions=None):
    highlight_positions = set(highlight_positions or [])

    # Set cell sizes
    cell_w, cell_h = 28, 28
    grid_w, grid_h = cols * cell_w, rows * cell_h
    img_w = grid_w + OUTER_PADDING * 2 + 60
    img_h = grid_h + OUTER_PADDING * 2 + 80

    # Canvas
    img = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font = ImageFont.truetype(FONT_PATH, 18)
        font_small = ImageFont.truetype(FONT_PATH, 15)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    left_x, top_y = OUTER_PADDING, OUTER_PADDING + 20

    # --- HEADER ---
    draw.text((left_x, 20), "54 - Essay Sheet", fill="black", font=font_small)
    draw.text((img_w - left_x - 270, 20), "Name: ____________________", fill="black", font=font_small)

    # --- DRAW GRID ---
    thin_color = (0,0,0,120)
    bold_color = (0,0,0,255)

    # Horizontal lines
    for r in range(rows + 1):
        y = top_y + r * cell_h
        width = BOLD_LINE_WIDTH if r % 4 == 0 else GRID_LINE_WIDTH
        color = bold_color if r % 4 == 0 else thin_color
        if r % 4 != 0:
            draw_dotted_line(draw, (left_x, y), (left_x + grid_w, y), spacing=6, width=1, fill=color)
        else:
            draw.line([(left_x, y), (left_x + grid_w, y)], fill=color, width=width)

    # Vertical lines
    for c in range(cols + 1):
        x = left_x + c * cell_w
        width = BOLD_LINE_WIDTH if c % 5 == 0 else GRID_LINE_WIDTH
        color = bold_color if c % 5 == 0 else thin_color
        if c % 5 != 0:
            draw_dotted_line(draw, (x, top_y), (x, top_y + grid_h), spacing=6, width=1, fill=color)
        else:
            draw.line([(x, top_y), (x, top_y + grid_h)], fill=color, width=width)

    # --- ROW NUMBERS EVERY 2 ROWS ---
    for r in range(2, rows+1, 2):
        number = 50 * (r // 2)
        y = top_y + r * cell_h - cell_h//3
        draw.text((left_x + grid_w + 5, y), str(number), fill="black", font=font_small)

    # --- TEXT IN CELLS ---
    for idx, ch in enumerate(text):
        row, col = divmod(idx, cols)
        if row >= rows:
            break
        x0 = left_x + col * cell_w
        y0 = top_y + row * cell_h
        # Reduce font for punctuation
        if ch in ".,!?;:()[]{}":
            font_to_use = font_small
        else:
            font_to_use = font
        bbox = draw.textbbox((0, 0), ch, font=font_to_use)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = x0 + (cell_w - w) / 2
        y = y0 + (cell_h - h) / 2
        color = "red" if (row, col) in highlight_positions else "black"
        draw.text((x, y), ch, font=font_to_use, fill=color)

    # --- FOOTER ---
    footer_en = "Please don't turn answer sheet horizontally, otherwise you will get 100 points. | EviD inc"
    footer_kr = "답안지를 가로로 돌리지 마세요, 그렇지 않으면 100점을 받습니다."
    draw.text((OUTER_PADDING, img_h - 80), footer_en, fill="black", font=font_small)
    draw.text((OUTER_PADDING, img_h - 50), footer_kr, fill="black", font=font_small)

        # --- Teacher's Mark Box ---
    mark_box_w, mark_box_h = 200, 25  # width and height of box
    mark_x = 500
    mark_y = img_h - 53
    # Draw rectangle for Teacher's Mark
    draw.rectangle(
        [(mark_x, mark_y), (mark_x + mark_box_w, mark_y + mark_box_h)],
        outline="black",
        width=1
    )
    # Label inside the box
    draw.text(
        (mark_x + 10, mark_y + 3),
        "Teacher's Mark / 성적      ",
        fill="black",
        font=font_small
    )

    return img

