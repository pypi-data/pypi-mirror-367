# adbauto/screen.py

import cv2
import numpy as np
import time
from adbauto.input import tap


def find_image(screenshot, image_path, threshold=0.95):
    """
    Finds an image in the screenshot using OpenCV template matching in grayscale.
    Returns the center coordinates of the matched image if found, otherwise None.
    """
    # Convert scrcpy to grayscale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)

    # Load template and convert to grayscale
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Template image not found at {image_path}")

    # Perform template matching
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return center

    return None

def find_all_images(screenshot, image_path, threshold=0.95):
    """
    Finds all images in the screenshot using OpenCV template matching in grayscale.
    Returns a list of the center coordinates of the matched images if found, otherwise None.
    """
    # Convert screenshot to grayscale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)

    # Load template and convert to grayscale
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Template image not found at {image_path}")

    h, w = template.shape[:2]

    # Perform template matching
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)

    # Find all locations with matching score above threshold
    locations = np.where(result >= threshold)

    # Convert to list of center coordinates
    matches = []
    for pt in zip(*locations[::-1]):  # Switch x and y
        center = (pt[0] + w // 2, pt[1] + h // 2)
        matches.append(center)

    return matches

def tap_image(device_id, screenshot, image_path, threshold=0.95, delay=0.1, random_delay=False):
    """
    Finds a image in the screenshot and taps it if found.
    Returns the coordinates of the tap or None if not found.
    """
    if random_delay:
        delay = np.random.uniform(0.05, 2)

    center = find_image(screenshot, image_path, threshold)
    if center:
        time.sleep(delay)
        tap(device_id, center[0], center[1])
        return center
    return None

def tap_img_when_visible(device_id, scrcpyClient, image_path, threshold=0.95, delay=0.1, random_delay=False, timeout=10):
    """
    Continuously checks for the image on the screen and taps it when found.
    Returns the coordinates of the tap or None if not found within timeout.
    """
    start_time = time.time()
    center = None
    if random_delay:
        delay = np.random.uniform(0.05, 2)

    while center is None:
        center = tap_image(device_id, scrcpyClient.last_frame, image_path, threshold, delay)

        if time.time() - start_time > timeout:
            break

    return center

def get_pixel_color(screenshot, x, y):
    """
    Returns the color of the pixel at (x, y) in the screenshot.
    """
    if x < 0 or y < 0 or x >= screenshot.shape[1] or y >= screenshot.shape[0]:
        raise ValueError("Coordinates are out of bounds of the screenshot")
    
    img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

    # Convert RGBA to RGB
    return tuple(img_rgb[y, x])  # Return RGB values