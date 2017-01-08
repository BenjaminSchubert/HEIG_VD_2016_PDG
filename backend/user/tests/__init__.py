from PIL import Image
from django.core.files import File
from io import BytesIO


def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
    """
    Creates and returns an image file.

    :param name: name of the file to create
    :param ext: extension the file will have
    :param size: size of the file
    :param color: color of the image
    :return: a File object with the file
    """
    file_obj = BytesIO()
    image = Image.new("RGBA", size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)
