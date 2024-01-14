import csv
import random
from os import getenv
from time import time

import requests
from dotenv import load_dotenv
from PIL import Image, ImageEnhance

from img_utils import ImageText

load_dotenv()

# Default values
FONT = "assets/lato.ttf"
BACKGROUND = "assets/background.jpg"
QUOTES_FILE = "assets/quotes.csv"
OUTPUT = f"results/{time()}.jpg"
W, H = 1080, 1350
TEXT_COLOR = (255, 255, 255)
STROKE_COLOR = "black"
STROKE_WIDTH = 3
MAX_WIDTH = W - 150
MAX_HEIGHT = H - 100
HEADERS = {"Authorization": getenv("PEXELS_KEY")}


def main():
    download_background()
    edit_background()
    quote, author = get_quote()
    print(f'Quote: "{quote}" {author}')
    add_text_to_img(quote, author)


def get_backgrounds(page: int = 1):
    params = {
        "query": "nature",
        "orientation": "portrait",
        "page": page,
        "per_page": "40",
    }

    return requests.get(
        "https://api.pexels.com/v1/search", params=params, headers=HEADERS
    ).json()


def download_background(page: int = 1):
    # Get list of images
    images = get_backgrounds(page).get("photos")

    if not images:
        raise Exception("API Error")

    # Choose random one
    img_id = random.choice(images)["id"]
    download_url = f"https://www.pexels.com/photo/{img_id}/download"
    print(f"Downloading image: {download_url.removesuffix('/download')}")

    # Download it
    response = requests.get(
        download_url,
        headers=HEADERS,
    )

    with open(BACKGROUND, "wb") as f:
        f.write(response.content)


def edit_background():
    # Resize background
    img = Image.open(BACKGROUND)
    img = img.resize((W, H))

    # Change brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.55)

    img.save(BACKGROUND)


def get_quote():
    # Get number of quotes and choose random one
    with open(QUOTES_FILE) as f:
        reader = csv.DictReader(f)
        rand_quote_num = random.randint(0, len(list(reader)) - 1)

    # Choose random quote
    with open(QUOTES_FILE) as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            if rand_quote_num == i:
                return row["Quote"], row["Author"] if row["Author"] else "Unknown"


def add_text_to_img(quote: str, author: str):
    # Calculate correct quote's width, height, font_size etc. by creating
    # temporary blank image with background's width and height
    im = ImageText((W, H), background=(255, 255, 255, 200))
    multiply = (len(quote) // 28) if (len(quote) // 28) >= 2 else 2
    font_size = im.get_font_size(quote, FONT, MAX_WIDTH, MAX_HEIGHT) * multiply
    quote_width, quote_height = im.write_text_box(
        (0, 0),
        quote,
        box_width=MAX_WIDTH,
        font_filename=FONT,
        font_size=font_size,
        color=TEXT_COLOR,
    )
    author_width, x = im.write_text_box(
        (0, 0),
        author,
        box_width=MAX_WIDTH,
        font_filename=FONT,
        font_size=45,
        color=TEXT_COLOR,
    )

    # Write text on image (quote and it's author)
    img = ImageText(BACKGROUND)
    x, y = img.write_text_box(
        ((W - quote_width) / 2, (H - quote_height) / 2 - 200),
        quote,
        box_width=MAX_WIDTH,
        font_filename=FONT,
        font_size=font_size,
        color=TEXT_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )
    img.write_text_box(
        ((W - author_width) / 2, (H - quote_height) / 2 - 70 + quote_height),
        author,
        box_width=MAX_WIDTH,
        font_filename=FONT,
        font_size=45,
        color=TEXT_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
    )

    img.save(OUTPUT)
    Image.open(OUTPUT).show()


if __name__ == "__main__":
    main()
