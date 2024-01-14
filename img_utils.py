from PIL import Image, ImageDraw, ImageFont


class ImageText(object):
    """
    Create ImageText object.

    Args:
        file_or_size (str or tuple): Either a filename or a tuple specifying the size of the image.
        mode (str, optional): The mode of the image.
        background (tuple, optional): The background color of the image.
        encoding (str, optional): The encoding used for text.
    """

    def __init__(
        self, file_or_size, mode="RGBA", background=(0, 0, 0, 0), encoding="utf8"
    ):
        """
        Add default values based if it's a filename or tuple specifying the size of an image.
        """
        if isinstance(file_or_size, str):
            self.filename = file_or_size
            self.image = Image.open(self.filename)
            self.size = self.image.size
        elif isinstance(file_or_size, (list, tuple)):
            self.size = file_or_size
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None

        self.draw = ImageDraw.Draw(self.image)
        self.encoding = encoding

    def save(self, filename=None):
        """
        Saves image to a file.

        Args:
            filename (str, optional): Name of the file to save the image. If not provided, the original filename will be used instead.
        """
        self.image.save(filename or self.filename)

    def get_font_size(self, text, font, max_width=None, max_height=None):
        """
        Get the appropriate font size for the given text, font, maximum width and height constraints.

        Args:
            text (str): The text to be displayed.
            font (ImageFont): The font to be used.
            max_width (int, optional): The maximum width constraint for the text.
            max_height (int, optional): The maximum height constraint for the text.

        Returns:
            int: The appropriate font size for the given constraints.

        Raises:
            ValueError: If either max_width or max_height is not provided.
        """
        if not max_width or not max_height:
            raise ValueError("You need to pass max_width and max_height")

        font_size = 1
        text_size = self.get_text_size(font, font_size, text)

        while True:
            if text_size[0] >= max_width or text_size[1] >= max_height:
                return font_size - 1

            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(
        self,
        xy,
        text,
        font_filename,
        font_size=11,
        color=(0, 0, 0),
        max_width=None,
        max_height=None,
        stroke_color=(0, 0, 0),
        stroke_width=0,
    ):
        """
        Write text onto the image at the specified location.

        Args:
            xy (tuple): The starting coordinates (x, y) for the text.
            text (str): The text to be written.
            font_filename (str): The filename of the font to be used.
            font_size (int, optional): The size of the font.
            color (tuple, optional): The color of the text
            max_width (int, optional): The maximum width constraint for the text.
            max_height (int, optional): The maximum height constraint for the text.
            stroke_color (tuple, optional): The color of the text stroke.
            stroke_width (int, optional): The width of the text stroke.

        Returns:
            tuple: The size of the written text (width, height).
        """
        x, y = xy

        text_size = self.get_text_size(font_filename, font_size, text)
        font = ImageFont.truetype(font_filename, font_size)

        if x == "center":
            x = (self.size[0] - text_size[0]) / 2
        if y == "center":
            y = (self.size[1] - text_size[1]) / 2

        self.draw.text(
            (x, y),
            text,
            font=font,
            fill=color,
            stroke_fill=stroke_color,
            stroke_width=stroke_width,
        )

        return text_size

    def get_text_size(self, font_filename, font_size, text):
        """
        Returns the size of the text, based on the specified font and its size.

        Args:
            font_filename (str): The filename of the font.
            font_size (int): The size of the font.
            text (str): The text for which the size needs to be calculated.

        Returns:
            tuple: The size of the text (width, height).
        """
        font = ImageFont.truetype(font_filename, font_size)

        return font.getsize(text)

    def write_text_box(
        self,
        xy,
        text,
        box_width,
        font_filename,
        font_size=11,
        color=(0, 0, 0),
        justify_last_line=False,
        stroke_color=(0, 0, 0),
        stroke_width=0,
    ):
        """
        Write text inside a box on the image.

        Args:
            xy (tuple): The starting coordinates (x, y) for the box.
            text (str): The text to be written.
            box_width (int): The width of the box.
            font_filename (str): The filename of the font to be used.
            font_size (int, optional): The size of the font. Defaults to 11.
            color (tuple, optional): The color of the text. Defaults to (0, 0, 0).
            justify_last_line (bool, optional): Whether to justify the last line of text. Defaults to False.
            stroke_color (tuple, optional): The color of the text stroke. Defaults to (0, 0, 0).
            stroke_width (int, optional): The width of the text stroke. Defaults to 0.

        Returns:
            tuple: The size of the box containing the written text (width, height).
        """
        x, y = xy

        lines = []
        line = []
        words = text.split()

        for word in words:
            new_line = " ".join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            text_height = size[1]

            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]

        if line:
            lines.append(line)

        lines = [" ".join(line) for line in lines if line]
        height = y

        for index, line in enumerate(lines):
            height += text_height
            total_size = self.get_text_size(font_filename, font_size, line)
            x_left = int(x + ((box_width - total_size[0]) / 2))
            self.write_text(
                (x_left, height),
                line,
                font_filename,
                font_size,
                color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
            )

        return (box_width, height - y)
