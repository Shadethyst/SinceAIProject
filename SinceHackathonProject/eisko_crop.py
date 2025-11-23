# import module
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtCore import pyqtSlot



class eisko_crop():
    def __init__():
        super.__init__()
            
    def crop_eisko(img):
        print("running crop_eisko")
        # Convert PIL Image to NumPy array for OpenCV operations.
        # PIL Image.open loads images in RGB format by default.
        img_np_rgb = np.array(img)

        # Convert to grayscale
        # Since img_np_rgb is RGB, convert from RGB to GRAY.
        test_img_gray = cv2.cvtColor(img_np_rgb, cv2.COLOR_RGB2GRAY)

        # Step 1: Apply edge detection (Canny Edge)
        edges = cv2.Canny(test_img_gray, 50, 150)

        # Step 2: Detect lines using Hough Line Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=350, maxLineGap=10)

        # Step 3: Filter out vertical lines (lines with nearly vertical slope)
        vertical_lines = []
        coord_vertical_lines = []
        coord_horizontal_lines = []
        if lines is not None: # It's good practice to check if lines were found
            for line_coords in lines:
                x1, y1, x2, y2 = line_coords[0]
                # A vertical line should have x1 close to x2.
                # The condition abs(x2 - x1) < 10 checks for vertical lines.
                if abs(x2 - x1) < 10:
                    vertical_lines.append((x1, y1, x2, y2))
                    coord_vertical_lines.append((x1, y1, x2, y2))
                else :
                    coord_horizontal_lines.append((x1, y1, x2, y2))

        # Step 4: Check for lines that are close together
        close_lines = []
        threshold = 30
        threshold2 = 10
        for i in range(len(vertical_lines)-1):
            for j in range(i + 2, len(vertical_lines)):
                x1_a, _, y1_a, _ = vertical_lines[i] # Get x-coordinate of the first line
                x1_b, _, y1_b, y2_b = vertical_lines[j] # Get x-coordinate of the second line
                if (y1_a - y2_b) < 0:
                    if abs(x1_a - x1_b) < threshold: # Compare x-coordinates of the lines
                        if abs(x1_a - x1_b) > threshold2: # Compare x-coordinates of the lines
                            close_lines.append((vertical_lines[i], vertical_lines[j]))

        # Find the edges of the croppee area
        alkupiste_hor = close_lines[0][0][0]
        alkupiste_ver = close_lines[0][0][1]
        loppupiste_hor = close_lines[0][0][2]
        loppupiste_ver = close_lines[0][0][3]
        ylaraja = img.size[1]
        alaraja = 0
        vasenraja = 0
        oikearaja = img.size[0]
        paatepisteet = (alkupiste_hor, alkupiste_ver, loppupiste_hor, loppupiste_ver)
        # Find the line above and below the first close line
        if lines is not None: # It's good practice to check if lines were found
            for line_coords in lines:
                x1, y1, x2, y2 = line_coords[0]
                # A vertical line should have x1 close to x2.
                # The condition abs(x2 - x1) < 10 checks for vertical lines.
                if abs(x2 - x1) < 10:
                    if x1 < alkupiste_hor: # vasen puoli
                        if x1 > vasenraja:
                            vasenraja = x1
                    if x1 > (loppupiste_hor + 100): # oikea puoli
                        if x1 < oikearaja:
                            oikearaja = x1
                else : # Line is horizontal
                    if y1 > alkupiste_ver:
                        if y1 < ylaraja:
                            ylaraja = y1
                    if y2 < loppupiste_ver:
                        if y2 > alaraja:
                            alaraja = y2
        cropped_image = img.crop((vasenraja, alaraja, oikearaja, ylaraja))

        return cropped_image


    def callOnContinue(path):
        # The path to PDF file:
        print("running callOnCreate")
        pdf_file_path = path
        images = convert_from_path(pdf_file_path)
        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save('page'+ str(i) +'.jpg', 'JPEG')

        img = Image.open(str(f"page{1}.jpg"))
        cropped = eisko_crop.crop_eisko(img)