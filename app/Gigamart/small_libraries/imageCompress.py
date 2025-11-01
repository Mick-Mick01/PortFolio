from PIL import Image
import io

def reduce_image_size(file_storage, max_size_mb=3, quality=85):
    """
    Reduces the size of an uploaded image to be <= max_size_mb.
    Returns a BytesIO object of the compressed image.

    Args:
        file_storage: werkzeug.datastructures.FileStorage object from Flask.
        max_size_mb: Maximum size in MB.
        quality: Initial JPEG quality.
    """
    max_bytes = max_size_mb * 1024 * 1024
    img = Image.open(file_storage)

    # Save compressed image to memory
    output_io = io.BytesIO()
    img.save(output_io, format=img.format, optimize=True, quality=quality)

    # Reduce quality until size fits
    while output_io.tell() > max_bytes and quality > 10:
        quality -= 5
        output_io.seek(0)
        output_io.truncate(0)
        img.save(output_io, format=img.format, optimize=True, quality=quality)

    output_io.seek(0)
    return output_io
