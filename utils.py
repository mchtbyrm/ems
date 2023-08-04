import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def resize_and_save_image(image, name, thumbnail=False, max_width=None, max_height=None, quality=100, format='JPEG'):
    img = Image.open(image).convert('RGB')

    # if image is a thumbnail, resize it to a specific size
    if thumbnail:
        size = (300, 300)
        img.thumbnail(size, Image.LANCZOS)
    else:
        size = (max_width, max_height)
        img.thumbnail(size, Image.LANCZOS)

    # Save the resized image to a new InMemoryUploadedFile
    output_image = BytesIO()
    img.save(output_image, format=format, quality=quality)
    output_image.seek(0)

    return InMemoryUploadedFile(output_image, 'ImageField', "%s.%s" % (name.split(".")[0], format.lower()),
                                f'image/{format.lower()}', sys.getsizeof(output_image), None)

