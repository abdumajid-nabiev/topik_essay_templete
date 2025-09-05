from PIL import Image, ImageDraw, ImageFont
import os

# Always load font relative to project roo
ROWS, COLS = 28, 25
GRID_LINE_WIDTH = 1        # thin, subtle lines
BOLD_LINE_WIDTH = 1        # slightly bolder lines
OUTER_PADDING = 25
CELL_PADDING = 2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "utils", "NotoSans.ttf")


def get_korean_font(size=24):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError as e:
        print("❌ Font not found or cannot be loaded:", e)
        return ImageFont.load_default()


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

