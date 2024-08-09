# py-metaimage
#
# Docs:
#   https://pillow.readthedocs.io/en/latest/handbook/overview.html
#  https://github.com/fengsp/color-thief-py

import datetime
from dataclasses import dataclass
import logging

from PIL import Image, ImageOps, ImageDraw, ImageFont, ExifTags
from colorthief import ColorThief

logger = logging.getLogger(__name__)

@dataclass
class Dimensions:
    """ Class for all the weird dimension calculations"""
    width: int = 640
    height: int = 800
    border_color: str = "white"
    border_topoffset = int = 0

    image_width: int = 600
    image_height: int = 0

    text1_y: int = 120
    text1_fontsize: str = 22
    text1_color: str = "Black"

    text2_y: int = 150
    text2_fontsize: str = 16
    text2_color: str = "Gray"

    text3_y: int = 120
    text3_fontsize: str = 18
    text3_color: str = "Black"

    text4_y: int = 150
    text4_fontsize: str = 16
    text4_color: str = "Gray"

    palette_position: int = 25
    palette_height: int = 75
    palette_count: int = 5

    def border_side(self):
        return round((self.width - self.image_width)/2)

    def border_top(self):
        return round((self.height - self.image_height + self.border_topoffset)/2)

    def border_bottom(self):
        return round((self.height - self.image_height - self.border_topoffset)/2)

    def palette_step(self):
        return round(self.image_width / self.palette_count)

    def palette_y(self):
        return self.border_top() + self.image_height + self.palette_position


d = Dimensions()


def read_exif_im(im: Image) -> dict:
    logging.info("Reading EXIF data from file: %s" % im.filename)
    logging.debug("Image format: %s Image size: %s Mode: %s" % (im.format, im.size, im.mode))

    exif = {
        ExifTags.TAGS[k]: v
        for k, v in im._getexif().items()
        if k in ExifTags.TAGS
    }
    logging.info("Exif data from the file are: %s" % exif)

    return exif


def read_exif_file(file: str) -> dict:
    im = Image.open(file)
    return read_exif_im(im)


def calculate_color_palette(file: str, palette_count: int) -> list:

    color_thief = ColorThief(file)

    dominant_color = color_thief.get_color(quality=1)
    logging.debug("Image dominant color: %s" % str(dominant_color))

    palette = color_thief.get_palette(color_count=5, quality=1)
    logging.info("Color palette: %s" % str(palette))

    return palette


def resize_image(im: Image, dims: Dimensions) -> Image:

    percent = (dims.image_width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(percent)))

    logging.info("Resizing image to: width %d x %d (%f percent)" % (dims.image_width, hsize, percent))

    im = im.resize((dims.image_width, hsize), Image.Resampling.LANCZOS)
    dims.image_height = hsize
    logging.debug("New image size: %s" % str(im.size))

    return im


def add_image_border(im: Image, dims: Dimensions) -> Image:

    bg_color = dims.border_color
    bg_border = (dims.border_side(), dims.border_top(), dims.border_side(), dims.border_bottom())
    logging.info("Border color: %s \nBorder size: %s" % (bg_color, bg_border))
    resized_im = ImageOps.expand(im, border=bg_border, fill=bg_color)
    logging.debug("New image size: %s" % str(im.size))

    return resized_im


def nice_shutter(exposure_time: float) -> str:
    exp = round(1 / exposure_time)
    return "1/%ss" % str(exp)


def add_text(im: Image, exif_data: dict, dims: Dimensions) -> Image:
    camera = str(exif_data["Model"])
    lens = str(exif_data["LensModel"])
    shot_info = "%smm f/%s %s ISO%s" % (
    exif_data["FocalLengthIn35mmFilm"], exif_data["ApertureValue"], nice_shutter(exif_data["ExposureTime"]), exif_data["ISOSpeedRatings"])
    shot_date = datetime.datetime.strptime(exif_data["DateTime"], "%Y:%m:%d %H:%M:%S").strftime("%H:%M:%S %Y:%m:%d")

    im_draw = ImageDraw.Draw(im)
    text1_font = ImageFont.truetype("fonts/Panamera-Black.ttf", dims.text1_fontsize)
    text2_font = ImageFont.truetype("fonts/Panamera-Black.ttf", dims.text2_fontsize)
    text3_font = ImageFont.truetype("fonts/Panamera-Black.ttf", dims.text3_fontsize)
    text4_font = ImageFont.truetype("fonts/Panamera-Black.ttf", dims.text4_fontsize)

    im_draw.text((dims.border_side(), dims.text1_y), camera, fill=dims.text1_color, font=text1_font, anchor="lt")
    im_draw.text((dims.border_side(), dims.text2_y), lens, fill=dims.text2_color, font=text2_font, anchor="lt")

    im_draw.text((dims.image_width + dims.border_side(), dims.text3_y), shot_info, fill=dims.text3_color, font=text3_font, anchor="rt")

    lenght = im_draw.textlength(shot_info, font=text3_font, )
    im_draw.text((dims.image_width + dims.border_side() - lenght, dims.text4_y), shot_date, fill=dims.text4_color, font=text4_font, anchor="lt")

    return im


def add_color_palette(im: Image, palette: list, dims: Dimensions, palette_reverse: bool = False) -> Image:
    im_draw = ImageDraw.Draw(im)

    if palette_reverse:
        palette.reverse()

    step = round(dims.image_width / dims.palette_count)

    for x in range(dims.border_side(), dims.image_width + dims.border_side(), step):
        im_draw.rectangle([(x, dims.palette_y()), (x + step, dims.palette_y() + dims.palette_height)], fill=palette.pop())

    return im


    return 0


def print_hi():
    im = Image.open("sample.jpg")
    print(im.format, im.size, im.mode)

    exifRaw = im.getexif()
    print(exifRaw)
    exif = {
        ExifTags.TAGS[k]: v
        for k, v in im._getexif().items()
        if k in ExifTags.TAGS
    }
    print(exif)
    print(exif["Model"])

    color_thief = ColorThief("sample.jpg")
    dominant_color = color_thief.get_color(quality=1)
    print(dominant_color)
    palette = color_thief.get_palette(color_count=5, quality=1)
    print(palette)

    base_width = 600
    wpercent = (base_width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((base_width, hsize), Image.Resampling.LANCZOS)
    print(im.size)

    bg_color = "white"
    bg_border = (20, 170, 20, 220)
    new_im = ImageOps.expand(im, border=bg_border, fill=bg_color)

    text_im = ImageDraw.Draw(new_im)
    myFont = ImageFont.truetype("fonts/Panamera-Black.ttf", 22)
    myFontMid = ImageFont.truetype("fonts/Panamera-Black.ttf", 18)
    myFontSmall = ImageFont.truetype("fonts/Panamera-Black.ttf", 16)

    text_im.text((36, 100), exif["Model"], fill="Black", font=myFont)
    text_im.text((36, 130), exif["LensModel"], fill="Gray", font=myFontSmall)

    # s3 = "%d %s" % (exif["FocalLengthIn35mmFilm"], exif["ApertureValue"], exif["ShutterSpeedValue"], exif["LensModel"], ["LensModel"])
    shotInfo = "%smm f/%s 1/%ss ISO%s" % (exif["FocalLengthIn35mmFilm"], exif["ApertureValue"], str(1/exif["ExposureTime"]), exif["ISOSpeedRatings"])
    # TODO: Round shutter speed to non decimal number
    print(shotInfo)

    text_im.text((380, 100), shotInfo, fill="Black", font=myFontMid)

    shotDate = datetime.datetime.strptime(exif["DateTime"], "%Y:%m:%d %H:%M:%S")
    print(shotDate.strftime("%H:%M:%S %Y:%m:%d"))

    text_im.text((380, 130), shotDate.strftime("%H:%M:%S %Y:%m:%d"), fill="Gray", font=myFontSmall)

    # text_im.rectangle([(20, 600), (20+120, 600+75)], fill=dominant_color)

    # palette.reverse()
    for x in range(20,620, 120):
        text_im.rectangle([(x, 600), (x + 120, 600 + 75)], fill=palette.pop())

    new_im.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()
    logging.basicConfig(level=logging.DEBUG)

# EOF
