import os
from PIL import Image, ImageDraw, ImageFont

# Canvas configuration
CANVAS_WIDTH = 720
CANVAS_HEIGHT = 405
CANVAS_COLOR = (255, 255, 255)  # White background fallback

# Background configuration
BG_FILENAME = "badges-background.png"

# Badge configuration
ORIGINAL_SIZE = (225, 225)
TARGET_SIZE = (270, 270)

# Placement coordinates
LEFT_X = 60
RIGHT_X = CANVAS_WIDTH - 60 - TARGET_SIZE[0]  # 390px
TOP_Y = 30
TEXT_Y = TOP_Y + TARGET_SIZE[1] + 15  # 360px
TEXT_WIDTH = 270

# Font configuration
FONT_PATH_REGULAR = "Lato-Regular.ttf"  # Ensure this file is in your directory
FONT_PATH_BOLD = "Lato-Bold.ttf"  # Ensure this file is in your directory
FONT_SIZE = 27
TEXT_COLOR = (0, 0, 0)  # Black text

# Club dataset mapping filenames to display names
clubs = {
    "biddenham.png": "Biddenham Cricket Club",
    "bedford.png": "Bedford Cricket Club",
    "dunstable.png": "Dunstable Town Cricket Club",
    "flitwick.png": "Flitwick Cricket Club",
    "ickwell.png": "Ickwell Cricket Club",
    "luton-town-and-indians.png": "Luton Town and Indians Cricket Club",
    "lutonian.png": "Lutonian Cricket Club",
    "queens-park-westfield.png": "Queen's Park Westfield Cricket Club",
    "southill-park.png": "Southill Park Cricket Club",
}


def wrap_text(text, font, max_width):
    """Wraps text cleanly based on pixel width rather than character count."""
    words = text.split(" ")
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        # Get width of the line using the font bounding box
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def draw_centred_wrapped_text(draw, text_wrapped, start_x, max_width, y_pos, font, fill_color):
    """Calculates the bounding box of multiline text and centers it horizontally within max_width."""
    # Get the bounding box of the entire multi-line text block
    box = draw.multiline_textbbox((start_x, y_pos), text_wrapped, font=font, align="center")
    text_width = box[2] - box[0]

    # Calculate how much space is left over in the 270px target box, and shift right by half of it
    remaining_space = max_width - text_width
    adjusted_x = start_x + (remaining_space // 2)

    # Draw the text with internal alignment set to center
    draw.multiline_text((adjusted_x, y_pos), text_wrapped, font=font, fill=fill_color, align="center")


def draw_versus_text(draw, font, fill_color):
    """Positions and draws the text 'vs.' perfectly dead-centre between the badges."""
    vs_text = "vs."

    # Find the geometric centre coordinates
    # Horizontal middle of the entire canvas
    mid_x = CANVAS_WIDTH // 2  # 360px
    # Vertical middle of the badges (Top position + half the target badge height)
    mid_y = TOP_Y + (TARGET_SIZE[1] // 2)  # 30 + 135 = 165px

    # Get the dimensions of the text to calculate offsets
    box = draw.textbbox((0, 0), vs_text, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    # Offset the positions so the middle of the text aligns with mid_x and mid_y
    vs_x = mid_x - (text_width // 2)
    vs_y = mid_y - (text_height // 2)

    draw.text((vs_x, vs_y), vs_text, font=font, fill=fill_color)


def create_fixture_image(left_filename, right_filename, output_filename):
    """Creates a single fixture image canvas, pastes badges, and writes centred text."""
    # Create blank canvas
    canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), CANVAS_COLOR)

    # Load and paste the full-bleed background image first
    bg_path = f"cricket_badges/input/{BG_FILENAME}"
    try:
        background = Image.open(bg_path).convert("RGB").resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)
        canvas.paste(background, (0, 0))
    except FileNotFoundError:
        print(f"Warning: Background image {bg_path} not found. Proceeding with white background.")

    # Initialize draw object after background is placed
    draw = ImageDraw.Draw(canvas)

    # Load regular font for club names
    try:
        font_regular = ImageFont.truetype(FONT_PATH_REGULAR, FONT_SIZE)
    except IOError:
        print(f"Font file {FONT_PATH_REGULAR} not found. Falling back to default font.")
        font_regular = ImageFont.load_default()

    # Load bold font for the "vs." text
    try:
        font_bold = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE)
    except IOError:
        print(f"Font file {FONT_PATH_BOLD} not found. Falling back to regular/default font.")
        font_bold = font_regular

    # Build the full paths for loading the files
    left_img_path = f"cricket_badges/input/{left_filename}"
    right_img_path = f"cricket_badges/input/{right_filename}"

    try:
        left_badge = Image.open(left_img_path).convert("RGBA").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        right_badge = Image.open(right_img_path).convert("RGBA").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    except FileNotFoundError as e:
        print(f"Skipping image generation: {e.filename} is missing.")
        return

    # Paste left badge (handles transparency if present)
    canvas.paste(left_badge, (LEFT_X, TOP_Y), left_badge)

    # Paste right badge
    canvas.paste(right_badge, (RIGHT_X, TOP_Y), right_badge)

    # Draw the central bold "vs." text
    draw_versus_text(draw, font_bold, TEXT_COLOR)

    # Get club names using the original filenames as keys
    left_name = clubs[left_filename]
    right_name = clubs[right_filename]

    # Wrap text to 270px boundaries
    left_text_wrapped = wrap_text(left_name, font_regular, TEXT_WIDTH)
    right_text_wrapped = wrap_text(right_name, font_regular, TEXT_WIDTH)

    # Draw horizontally centred text blocks using the helper function
    draw_centred_wrapped_text(draw, left_text_wrapped, LEFT_X, TEXT_WIDTH, TEXT_Y, font_regular, TEXT_COLOR)
    draw_centred_wrapped_text(draw, right_text_wrapped, RIGHT_X, TEXT_WIDTH, TEXT_Y, font_regular, TEXT_COLOR)

    # Save output as WebP with quality=50
    canvas.save(output_filename, "WEBP", quality=50)
    print(f"Saved: {output_filename}")


def main():
    home_team_file = "biddenham.png"
    opponents = [img for img in clubs.keys() if img != home_team_file]

    # Ensure output directory exists
    os.makedirs("cricket_badges/output", exist_ok=True)

    # Round 1: Biddenham at Home (Left side)
    print("Generating Round 1 (Biddenham Home matches)...")
    for opponent in opponents:
        opponent_clean_name = opponent.replace(".png", "")
        output_name = f"cricket_badges/output/1_home_biddenham_vs_{opponent_clean_name}.webp"
        create_fixture_image(home_team_file, opponent, output_name)

    # Round 2: Biddenham Away (Right side)
    print("\nGenerating Round 2 (Biddenham Away matches)...")
    for opponent in opponents:
        opponent_clean_name = opponent.replace(".png", "")
        output_name = f"cricket_badges/output/2_away_{opponent_clean_name}_vs_biddenham.webp"
        create_fixture_image(opponent, home_team_file, output_name)


if __name__ == "__main__":
    main()
