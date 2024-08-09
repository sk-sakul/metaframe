# py-metaimage
#
# Docs:
#   https://pillow.readthedocs.io/en/latest/handbook/overview.html
#  https://github.com/fengsp/color-thief-py

import datetime
from dataclasses import dataclass

from PIL import Image, ImageOps, ImageDraw, ImageFont, ExifTags
from colorthief import ColorThief


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


def read_exif_data():
    return 0


def calculate_color_palette():
    return 0


def resize_image():
    return 0


def add_image_border():
    return 0


def add_text():
    return 0


def add_color_palette():
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

# EOF
