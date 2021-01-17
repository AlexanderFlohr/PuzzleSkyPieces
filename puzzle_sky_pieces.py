from PIL import Image, ImageFilter


# Two possible modes:
# PIECE: Consider single pieces as uniform entities
# PIXEL: Consider each pixel as widely independent entity (not runtime optimized)
mode = "PIECE"

# manually define the input an output image
filein = "16.jpg"
fileout = "16.png"

# predefined color
if mode == "PIXEL":
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
else:
    black = (32,32,32)
    red = (191, 8, 8)
    green = (8, 191, 51)
    blue = (8, 93, 191)
    white = (226, 226, 226)

# manually tune the pixel thresholds (must be monotonically increasing)
# adjust them to alter the amount of resulting red, green, blue, and white pieces
t1 = 0.24
t2 = 0.52
t3 = 0.77


####################################################################################
################################# General functions ################################
####################################################################################


def is_gray(r, g, b, variance=0.1):
    """
    Check if the given RGB values result in a gray pixel.
    """

    # sort RGB values to reduce number of checks
    pixel = [r, g, b]
    pixel.sort()

    # check if the given RGB values lie outside a certain gray-interval
    if pixel[0] <= sum(pixel)/3 - 255 * variance:
        return False

    if pixel[2] >= sum(pixel)/3 + 255 * variance:
        return False

    # otherwise, its gray
    return True


def is_blue(r, g, b):
    """
    Check if the given RGB value encodes for blue, i.e. check if blue is dominant.
    """

    return b > r and b > g


####################################################################################
############################### PIECE-mode functions ###############################
####################################################################################

# for PIECE-mode, load the image in advance
if mode == "PIECE":
    # load the image and its dimensions
    img = Image.open("Images/" + filein)
    pix = img.load()
    width, height = img.size

    # required for PIECE-model solely
    blue_pixels = set()
    blues = list()
    gray_pixels = set()
    pieces = dict()
    votes = dict()


def expand_piece(k, h, w):
    """
    Detect all neighboring pixels that belong to the same puzzle-piece.
    This process is performed iteratively.
    """

    # setup a new piece
    pieces[k] = list()
    neighbors = set()
    neighbors.add((h, w))

    # search until their is no fitting neighbor left
    while len(neighbors) > 0:
        h, w = neighbors.pop()

        # assess the RGB values
        r, g, b = pix[w, h]

        # check the color-criteria
        if (h, w) in blue_pixels:
            continue
        if (h, w) in gray_pixels:
            continue

        # again store unfitting pixels to avoid endless loops
        if is_gray(r, g, b):
            gray_pixels.add((h, w))
            continue

        # if a pixel is blue, store it as such and add the its neighbors to the queue
        if is_blue(r, g, b):
            pieces[k].append((h, w, b))
            blues.append(b)
            blue_pixels.add((h, w))
            for i in range(max(0, w - 1), min(width, w + 2)):
                for j in range(max(0, h - 1), min(height, h + 2)):
                    if(j, i) not in blue_pixels:
                        neighbors.add((j, i))
        else:
            gray_pixels.add((h, w))
            continue


def detect_pieces():
    """
    Detect all pussle-pieces, i.e. separate blue areas
    """

    for w in range(0, width):
        for h in range(0, height):

            # is a pixel is known to be blue or gray, move on
            if (h, w) in blue_pixels:
                continue
            if (h, w) in gray_pixels:
                continue

            # otherwise it could be a new puzzle-piece
            r, g, b = pix[w, h]
            if is_gray(r, g, b):
                gray_pixels.add((h, w))
                continue

            # actual new piece
            if is_blue(r, g, b):
                expand_piece(len(pieces.keys()), h, w)
            else:
                gray_pixels.add((h, w))
                continue


def get_quartiles():
    """
    Assess the previously stored blue-values, and compute lower, medium, and upper quartile
    """

    blues.sort()
    print(blues)
    return blues[round(len(blues)*t1)], blues[round(len(blues)*t2)], blues[round(len(blues)*t3)]


def majority_vote(low, medium, high):
    """
    Color the pixel according to the most common pixel classification, relative
    to the given lower, medium, and upper quartile
    """

    for k in pieces.keys():
        scores = [[red, 0],[green, 0],[blue, 0],[white, 0]]
        for w, h, b in pieces[k]:
            if b < low:
                scores[0][1] += 1
            elif b < medium:
                scores[1][1] += 1
            elif b < high:
                scores[2][1] += 1
            else:
                scores[3][1] += 1
        scores.sort(key=lambda x: x[1], reverse=True)
        print(scores)
        votes[k] = scores[0][0]


def recolor():
    """
    Recolor the image to enable color-based piece separation
    """

    for h, w in gray_pixels:
        pix[w, h] = black

    # piece colors are defined during majority vote
    for k in pieces.keys():
        color = votes[k]
        for h, w, b in pieces[k]:
            pix[w, h] = color


if mode == "PIECE":
    print("1. Search for puzzle pieces")
    detect_pieces()
    print("  -> " + str(len(pieces.keys())) + " pieces detected")

    print("2. Compute quartiles")
    q25, q50, q75 = get_quartiles()

    print("3. Perform majority votes")
    majority_vote(q25, q50, q75)

    print("3. Recolor puzzle pieces")
    recolor()

    print("4. Save new image")
    img.save("./Images/test" + fileout)
    exit(0)


####################################################################################
############################### PIXEL-mode functions ###############################
####################################################################################

def paint_black(t=0.1):
    """
    Repaint all none-blue pixels black
    """

    for w in range(0, width):
        for h in range(0, height):
            r, g, b = pix[w, h]
            gray = is_gray(r, g, b, variance=t)

            if gray or not is_blue(r, g, b):
                pix[w, h] = black


def smooth_image(pic, repeats=10):
    """
    Smooth the image to reduce pixel-snow
    """

    while repeats > 0:
        pic = pic.filter(ImageFilter.MedianFilter)
        repeats -= 1
    return pic


def normalize(pic):
    """
    Modify all blue pixels such that the darkest blue is assigned to
    value 0, vice versa, the brightest one should become 255
    """

    # Copy the image for better accessibility
    img2 = pic.copy()
    pix2 = img2.load()

    # temporarily store all blue values
    blues = list()
    for w in range(2, width - 2):
        for h in range(2, height - 2):
            r, g, b = pix[w, h]

            if not is_gray(r, g, b):
                if is_blue(r, g, b):
                    blues.append(b)

    # sort them for statistical evaluations
    blues.sort()

    # compute the brightest and darkest blue values
    # for robustness, ignore the brightest and darkest 1% (outlier)
    minimum = int(blues[int(len(blues)*0.01)])
    maximum = int(blues[int(len(blues)*0.99)])

    # scale factor, required to stretch the blue range
    factor = 255/(maximum-minimum)

    # update each pixel of the image according to the upper stretching values
    for w in range(2, width - 2):
        for h in range(2, height - 2):
            r, g, b = pix[w, h]
            if not is_gray(r, g, b):
                if is_blue(r, g, b):
                    pix2[w, h] = (0, 0, min(255, max(0, int((b-minimum)*factor))))

    # access and return the quartiles
    c1 = min(255, max(0, (int(blues[int(t1 * len(blues))]) - minimum) * factor))
    c2 = min(255, max(0, (int(blues[int(t2 * len(blues))]) - minimum) * factor))
    c3 = min(255, max(0, (int(blues[int(t3 * len(blues))]) - minimum) * factor))
    return img2, c1, c2, c3


def color_it(pic, c1, c2, c3):
    """
    Recolor each blue pixel according to the given thresholds
    """

    pix2 = pic.load()
    for w in range(0, width):
        for h in range(0, height):
            r, g, b = pix2[w, h]

            # update the color of the given blue pixel
            if not is_gray(r, g, b):
                if is_blue(r, g, b):
                    if b < c1:
                        pix2[w,h] = red
                    elif b < c2:
                        pix2[w,h] = green
                    elif b < c3:
                        pix2[w,h] = blue
                    else:
                        pix2[w, h] = white
    return img


if mode == "PIXEL":
    # load the image and its properties
    img = Image.open("Images/" + filein)
    pix = img.load()
    width, height = img.size

    print("1. Overwrite gray areas")
    paint_black()

    print("2. Smooth the image")
    img = smooth_image(img, repeats=40)

    print("3. Normalize the image")
    img, i1, i2, i3 = normalize(img)

    print("5. Recolor blue pixels")
    img = color_it(img, i1, i2, i3)

    print("6. Smooth the image")
    img = smooth_image(img, repeats=20)

    print("6. Save image")
    img.save("./Images/" + fileout)
