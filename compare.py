from PIL import Image, ImageChops

PIXEL_TOLERANCE = 30
CHANGE_THRESHOLD = 0.1


def pad_to_size(image, size):
    canvas = Image.new("RGB", size, "white")
    canvas.paste(image, (0, 0))
    return canvas


def compare_screenshots(before_path, after_path, diff_path=None):
    before = Image.open(before_path).convert("RGB")
    after = Image.open(after_path).convert("RGB")
    size_changed = before.size != after.size

    size = (max(before.width, after.width), max(before.height, after.height))
    before = pad_to_size(before, size)
    after = pad_to_size(after, size)

    diff = ImageChops.difference(before, after).convert("L")
    mask = diff.point(lambda value: 255 if value > PIXEL_TOLERANCE else 0)

    total_pixels = size[0] * size[1]
    changed_pixels = mask.histogram()[255]
    change_percentage = changed_pixels / total_pixels * 100

    if diff_path and changed_pixels > 0:
        red = Image.new("RGB", size, "red")
        Image.composite(red, after, mask).save(diff_path)

    return {
        "changed": size_changed or change_percentage > CHANGE_THRESHOLD,
        "size_changed": size_changed,
        "change_percentage": round(change_percentage, 3),
        "changed_area": mask.getbbox(),
    }