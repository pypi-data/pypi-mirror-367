from io import BytesIO

import requests
from PIL import Image, ImageDraw


def download_image(url, size=(224, 224)):
    """Download image from URL and resize it."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return img.resize(size)
    except Exception as e:
        print(f"Failed to load {url}: {e}")
        # Return a gray placeholder
        return Image.new("RGB", size, (200, 200, 200))


def create_grid_from_url_lists(
    url_grid, input_url, save_path="concept_grid.jpg", img_size=(224, 224)
):
    """
    Creates a single image:
      - Left: grid of concept rows (each row is a concept, columns are retrieved images)
      - Right: one large input image

    Args:
        url_grid (List[List[str]]): list of rows, where each row is a list of image URLs
        input_url (str): URL of the big input image shown on the right side
        save_path (str): where to save the final grid image
        img_size (tuple): width, height of each thumbnail in the grid
    """
    all_concept_images = []
    max_cols = 0

    # Download all concept grid images
    for row_urls in url_grid:
        row_images = [download_image(url, size=img_size) for url in row_urls]
        all_concept_images.append(row_images)
        max_cols = max(max_cols, len(row_images))

    # Grid size
    num_rows = len(all_concept_images)
    thumb_w, thumb_h = img_size
    grid_width = max_cols * thumb_w
    grid_height = num_rows * thumb_h

    # Download input image (resize proportionally to match grid height)
    input_img = download_image(input_url)

    # Maintain aspect ratio for input image but match grid height
    aspect_ratio = input_img.width / input_img.height
    input_resized = input_img.resize((int(grid_height * aspect_ratio), grid_height))

    # Final canvas width = grid width + input image width
    final_width = grid_width + input_resized.width
    final_height = grid_height

    # Create final canvas
    final_img = Image.new("RGB", (final_width, final_height), color=(255, 255, 255))

    # Paste grid images
    for row_idx, row_images in enumerate(all_concept_images):
        for col_idx, img in enumerate(row_images):
            x = col_idx * thumb_w
            y = row_idx * thumb_h
            final_img.paste(img, (x + input_resized.width, y))

    # Paste the input image to the RIGHT of the grid
    final_img.paste(input_resized, (0, 0))

    # Save the result
    final_img.save(save_path)
    print(f"✅ Saved combined grid + input image to {save_path}")
