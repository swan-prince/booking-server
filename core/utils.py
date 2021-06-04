import os
from io import BytesIO
from PIL import Image
from django.core.files import File

PAGINATE_BY = 10
THUMBNAIL_SIZE = (100, 100)

def resize_image(image, size=(100, 100), thumbnail=False):
    """Makes thumbnails of given size from given image"""
    image_path = image.path
    img = Image.open(image_path)
    img.thumbnail(size) # resize image
    img.save(image_path)

    if thumbnail:
        dirname = os.path.dirname(image_path)
        basename = os.path.basename(image_path)
        thumbnail_path = os.path.join(dirname, 'thumbnail', basename)

        if not os.path.exists(os.path.join(dirname, 'thumbnail')):
            os.makedirs(os.path.join(dirname, 'thumbnail'))

        img = Image.open(image_path)
        img.thumbnail(THUMBNAIL_SIZE) # resize image
        img.save(thumbnail_path)


def make_thumbnail(image, size=(100, 100)):
    """Makes thumbnails of given size from given image"""

    im = Image.open(image)
    im.convert('RGB') # convert mode
    im.thumbnail(size) # resize image
    thumb_io = BytesIO() # create a BytesIO object
    im.save(thumb_io, 'JPEG', quality=85) # save image to BytesIO object
    thumbnail_ext = image.name.split(".")[-1]
    thumbnail_name = ('.').join(image.name.split('.')[:-1])
    thumbnail_name += "_thumb." + thumbnail_ext

    thumbnail = File(thumb_io, name=thumbnail_name) # create a django friendly File object
    return thumbnail