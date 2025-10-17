import cv2
import numpy as np

# ======== Config ========
# Number of stickers per side (2, 3, 4, ...)
cube_size = 5
# HSV ranges for Rubik's cube colors (tune as needed)
COLOR_RANGES = {
    "white": [(0, 0, 80), (180, 100, 255)],
    "yellow": [(25, 100, 80), (35, 255, 255)],
    "red": [(0, 100, 80), (5, 255, 255)],
    "orange": [(5, 100, 80), (10, 255, 255)],
    "blue": [(90, 100, 80), (110, 255, 255)],
    "green": [(50, 100, 80), (60, 255, 255)]
}


def detect_color(hsv_pixel):
    """Map an HSV pixel to a cube color name."""
    for color, (lower, upper) in COLOR_RANGES.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(np.uint8([[hsv_pixel]]), lower_np, upper_np)
        if mask[0][0] == 255:
            return color
    return "unknown"


# ======== Step 1: Load image ========
# Load the input image
img = cv2.imread("cube2.jpeg")
if img is None:
    raise FileNotFoundError("Image not found. Make sure 'cube.jpeg' exists.")

# ======== Step 1.1: Color mask to focus on cube colors ========
# Convert to grayscale and HSV
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv_full = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Create mask for all cube colors
cube_mask = np.zeros(gray.shape, dtype=np.uint8)
for color, (lower, upper) in COLOR_RANGES.items():
    lower_np = np.array(lower, dtype=np.uint8)
    upper_np = np.array(upper, dtype=np.uint8)
    mask = cv2.inRange(hsv_full, lower_np, upper_np)
    cube_mask = cv2.bitwise_or(cube_mask, mask)

# Morphological closing and dilation to connect cube pieces
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
cube_mask = cv2.morphologyEx(cube_mask, cv2.MORPH_CLOSE, kernel)
cube_mask = cv2.dilate(cube_mask, kernel, iterations=2)

# Mask the grayscale image
masked_img = cv2.bitwise_and(gray, gray, mask=cube_mask)

# ======== Step 1.2: Find cube region ========
blurred = cv2.GaussianBlur(masked_img, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)
contours, _ = cv2.findContours(cube_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)
cube_rect = None
if contours:
    x, y, w, h = cv2.boundingRect(contours[0])
    cube_rect = (x, y, w, h)
if cube_rect:
    x, y, w, h = cube_rect
    # Show detected region for debug
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0,255,0), 2)
    cv2.imshow("Detected Cube Region", debug_img)
    img = img[y:y+h, x:x+w]
else:
    print("Warning: Cube not found, using full image.")

# ======== Step 2: Detect colors in grid ========
# Convert cropped image to HSV
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
height, width = hsv_img.shape[:2]
grid_colors = []
for i in range(cube_size):
    row_colors = []
    for j in range(cube_size):
        # Calculate grid cell coordinates
        y1, y2 = int(i * height / cube_size), int((i + 1) * height / cube_size)
        x1, x2 = int(j * width / cube_size), int((j + 1) * width / cube_size)
        # Take center 20% area of each cell
        cy1, cy2 = int(y1 + 0.4 * (y2 - y1)), int(y1 + 0.6 * (y2 - y1))
        cx1, cx2 = int(x1 + 0.4 * (x2 - x1)), int(x1 + 0.6 * (x2 - x1))
        roi = hsv_img[cy1:cy2, cx1:cx2]
        mean_hsv = np.mean(roi.reshape(-1, 3), axis=0).astype(int)
        print(f"HSV at ({i},{j}): {mean_hsv}")  # Debug print
        color_name = detect_color(mean_hsv)
        row_colors.append(color_name)
        # Draw color name on image
        cv2.putText(img, color_name, (x1 + 5, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    grid_colors.append(row_colors)

# ======== Step 3: Show results ========
print(f"Detected colors ({cube_size}x{cube_size}):")
for row in grid_colors:
    print(row)

# Show result images
cv2.imshow("Cube Colors", img)
cv2.imshow("Cube Mask", cube_mask)  # Show mask for debug
cv2.waitKey(0)
cv2.destroyAllWindows()
