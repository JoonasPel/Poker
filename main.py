# pylint: disable=C0115, C0103, C0116, C0114
import sys
import os
import time
import pygetwindow as gw
import pyautogui
from PIL import Image
import cv2
import numpy as np

IMAGES_DIR = "images"
title_prefix = "No Limit Hold'em"
# title_prefix = "Code"
rel_x_left_card = 0.44
rel_x_right_card = 0.503
rel_x = 0.504
rel_y = 0.622
rel_width = 0.0245
rel_height = 0.06

names = []
images = []

class NoWindowFound(Exception):
    pass

def read_images_to_arrays():
    for filename in os.listdir(IMAGES_DIR):
        if filename.endswith(".png"):
            path = os.path.join(IMAGES_DIR, filename)
            images.append(cv2.imread(path))
            names.append(filename)
    return images

# def read_images_to_descriptors():
#     print("Reading images to descriptors")
#     descriptors = []
#     for filename in os.listdir(IMAGES_DIR):
#         if filename.endswith(".png"):
#             path = os.path.join(IMAGES_DIR, filename)
#             image = cv2.imread(path)
#             desc = compute_sift(image)[1]
#             if isinstance(desc, np.ndarray):
#                 descriptors.append(desc)
#     print("Ready\n")
#     return descriptors

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def find_best_match(screenshot, images):
    best_err = 100000000000000
    pred = "No pred"
    for idx, image in enumerate(images):
        err = mse(screenshot, image)
        if err < best_err:
            best_err = err
            pred = names[idx]
    return pred, best_err


# def compute_sift(pil_image):
#     np_image = np.array(pil_image)
#     # Convert RGB to BGR (OpenCV uses BGR by default)
#     if np_image.ndim == 3:
#         np_image = np_image[:, :, ::-1]
#     gray_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
#     sift = cv2.SIFT_create()
#     keypoints, descriptors = sift.detectAndCompute(gray_image, None)
#     return keypoints, descriptors

# def compute_match_percentage(descriptors1, descriptors2):
#     bf = cv2.BFMatcher()
#     matches = bf.knnMatch(descriptors1, descriptors2, k=2)
#     good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
#     if len(matches) == 0:
#         match_percentage = 0
#     else:
#         match_percentage = (len(good_matches) / len(matches)) * 100
#     return match_percentage

def get_stars_window_title():
    titles: list[str] = gw.getAllTitles()
    for title in titles:
        if title_prefix in title:
            return title
    raise NoWindowFound("No Stars window found")

def handle_screenshot(screenshot_raw, is_left_card):
    if is_left_card:
        suffix = "left"
    else:
        suffix = "right"
    size = screenshot_raw.size
    if size != (37, 64):
        print(f"size is {size}. it should be (37, 64). Please adjust window.")
        screenshot_resize = screenshot_raw.resize((37, 64), Image.NEAREST)
    else:
        screenshot_resize = screenshot_raw
    screenshot = np.array(screenshot_resize)
    pred, err = find_best_match(screenshot, images)
    print(f"{suffix} -> pred: {pred}. err: {err}")
    if err > 1500:
        print("new card found")
        file_name = f"screenshot_{int(time.time())}_{suffix}.png"
        path = os.path.join(IMAGES_DIR, file_name)
        screenshot_resize.save(path)
        images.append(screenshot)
        names.append("unnamed")

def main():
    read_images_to_arrays()
    while True:
        input("Press Enter to continue...\n")
        try:
            window_title = get_stars_window_title()
            window = gw.getWindowsWithTitle(window_title)[0]
            window_width = window.width
            window_height = window.height
            top = window.top + int(window_height * rel_y)
            width = int(window_width * rel_width)
            height = int(window_height * rel_height)

            # left card
            left = window.left + int(window_width * rel_x_left_card)
            screenshot_left = pyautogui.screenshot(region=(left, top, width, height))
            handle_screenshot(screenshot_left, is_left_card=True)

            # right card
            left = window.left + int(window_width * rel_x_right_card)
            screenshot_right = pyautogui.screenshot(region=(left, top, width, height))
            handle_screenshot(screenshot_right, is_left_card=False)

        except IndexError as e:
            print(f"Window with title not found: {e}")
        except NoWindowFound as e:
            print(e)
        except Exception as e:
            print(f"Unknown problem: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
