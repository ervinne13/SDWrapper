from PIL import Image, ImageDraw, ImageFont

def add_watermark(
    image_path: str,
    output_path: str,
    text: str = "© YourName",
    position: str = "bottom_right",
    opacity: int = 128,
    margin: int = 10,
    font_size: int = 24
):
    """
    Adds a semi-transparent text watermark to an image.

    :param image_path: Input image path
    :param output_path: Path to save watermarked image
    :param text: Watermark text
    :param position: One of ["top_left", "top_right", "bottom_left", "bottom_right"]
    :param opacity: Transparency (0=transparent, 255=solid)
    :param margin: Padding from edges
    :param font_size: Font size in pixels
    """
    img = Image.open(image_path).convert("RGBA")
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))

    draw = ImageDraw.Draw(txt_layer)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Needs ttf installed
    except IOError:
        font = ImageFont.load_default()

    text_size = draw.textbbox((0, 0), text, font=font)
    text_w = text_size[2] - text_size[0]
    text_h = text_size[3] - text_size[1]

    if position == "top_left":
        pos = (margin, margin)
    elif position == "top_right":
        pos = (img.width - text_w - margin, margin)
    elif position == "bottom_left":
        pos = (margin, img.height - text_h - margin)
    else:  # bottom_right default
        pos = (img.width - text_w - margin, img.height - text_h - margin)

    draw.text(pos, text, font=font, fill=(255, 255, 255, opacity))

    watermarked = Image.alpha_composite(img, txt_layer).convert("RGB")
    watermarked.save(output_path, "PNG")
    print(f"✅ Watermarked saved to {output_path}")
