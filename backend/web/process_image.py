from pyqumit.string import mini_uuid
from pathlib import Path
from PIL import Image


def process_image(
    stream, 
    target_dir: Path,
    max_dimention: int = 800,
):
    image = Image.open(stream)
    if image.format not in ["PNG", "JPG", "JPEG"]:
        return None
    elif image.format == "PNG":
        image = image.convert('RGB')
        
    (width, height) = image.size
    if (max_dimention / width < max_dimention / height):
        factor = max_dimention / height
    else:
        factor = max_dimention / width

    size = (int(width / factor), int(height / factor))
    img_id = mini_uuid(sugar=30)
    image.resize(size).save(target_dir / f"{img_id}.jpg", quality = 80)
    return img_id
