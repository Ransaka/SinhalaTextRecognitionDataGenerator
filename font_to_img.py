from pathlib import Path
from typing import Union
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps, ImageFilter
import cv2
import numpy as np
from tqdm import tqdm
import warnings
import random

warnings.filterwarnings("ignore")

def postprocess_image(img:Image,color:str,blur_radius=0.5):
    # convert all non zero pixels to 255
    img = Image.eval(img, lambda px: 255 if px != 0 else 0)
    # blur the image
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # concert to L mode
    img = img.convert("L")
    # convert to RGBA
    img = ImageOps.colorize(img,black="black", white=color)
    return perspective_transform(img)

def perspective_transform(image:Image):
    # convert to numpy array
    image = np.array(image)
    original_points = np.float32([[0, 0], [image.shape[1], 0], [image.shape[1], image.shape[0]], [0, image.shape[0]]])
    new_points = np.float32([[0, 0], [image.shape[1], 0], [image.shape[1] * 0.8, image.shape[0]], [image.shape[1] * 0.2, image.shape[0]]])
    perspective_matrix = cv2.getPerspectiveTransform(original_points, new_points)
    perspective_image = cv2.warpPerspective(image, perspective_matrix, (image.shape[1], image.shape[0]))
    return Image.fromarray(perspective_image)

def generate_random_color_dark():
    # Generate random values for the red, green, and blue channels
    red = random.randint(0, 19)    # Keep these values in a range that produces dark colors
    green = random.randint(0, 19)  # Keep these values in a range that produces dark colors
    blue = random.randint(0, 19)   # Keep these values in a range that produces dark colors
    
    # Convert the RGB values to a hex color code
    hex_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)
    
    return hex_color

def generate_random_color()->str:
    return "#"+''.join([random.choice("0123456789ABCDEF") for j in range(6)])

def randomize_parameters(N):
    fonts = Path("fonts/sin").glob("*.ttf")
    font_filepath_array = [np.random.choice(fonts) for i in range(N)]
    color_array = [generate_random_color() for i in range(N)]
    font_size_array = [np.random.randint(20,50) for i in range(N)]
    perspective_transform_array = [np.random.choice([True,False]) for i in range(N)]
    background_image_path_array = [np.random.choice(list(Path("background").glob("*.jpg"))) for i in range(N)]
    parameters = {
        "font_filepath":font_filepath_array,
        "color":color_array,
        "font_size":font_size_array,
        "perspective_transform":perspective_transform_array,
        "background_image_path":background_image_path_array,
    }
    return parameters

def text_to_image(
    text: str,
    font_filepath: str,
    font_size: int,
    mask_background_color: Union[str, tuple] = "#FFFFFF",
    color: Union[str, tuple] = "#000000",
    font_align="center",
    rotate=1):

    font = ImageFont.truetype(font_filepath, size=font_size)
    box = font.getsize_multiline(text)
    img = Image.new("RGBA", (box[0], box[1]))

    #add padding
    img = Image.new("RGBA", (box[0]+int(font_size/4), box[1]+int(font_size/4)))
    # create image mask
    img_mask = Image.new("L", img.size, color=mask_background_color)

    draw = ImageDraw.Draw(img)
    draw_point = (0, 0)
    draw.multiline_text(draw_point, text, font=font, fill=color, align=font_align,embedded_color=True,stroke_fill = "#282828")
    if rotate:
        img = img.rotate(rotate, expand=True)
        # img.save(f"out/without_smoothing_{id}.png")
        # img = postprocess_image(img, blur_radius=0.5, color=color)
        img_mask = img_mask.rotate(rotate, expand=True,resample=Image.BICUBIC)
        rotate_angle = rotate
    else:
        rotate_angle = 0
    img = postprocess_image(img, blur_radius=0.5, color=color)
    return img, img_mask,rotate_angle

def main(text,background_img_path,font_path,font_size,color,shape=(512,512),rotate_flag=False):
    color = generate_random_color_dark()
    mask_background_color =  "white"
    if rotate_flag:
        rotate = np.random.randint(-15,15)
    else:
        rotate = rotate_flag
        
    results = [text_to_image(
        text=i.replace(" ",""),
        font_filepath=font_path,
        font_size=font_size,
        mask_background_color=mask_background_color,
        color=color,
        rotate=rotate
        ) for i in text.split()
        ]
    text_images = [i[0] for i in results]
    masks = [i[1] for i in results]
    
    # combine images
    # for image,mask in zip(text_images,masks):
    #     image.paste(mask, mask=mask)

    add_background(images = text_images,background_image_path = background_img_path,shape = shape,rotate_angle = rotate,masks=masks, rotate=rotate)

def add_background(images, background_image_path, shape, rotate_angle,masks, rotate=True):
    x_offset, y_offset = 10, 10
    max_height_by_row = -1

    # Read background image
    background = cv2.imread(background_image_path)
    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGBA)

    # Resize background image
    background = cv2.resize(background, (shape[1], shape[0]))

    # Convert PIL images to RGBA
    images = [i.convert("RGBA") for i in images]

    # Convert background to PIL image
    background = Image.fromarray(background)
    # background_height, background_width = background.size[1], background.size[0]

    #create a new background for mask
    background_mask = Image.new("RGBA", (shape[1], shape[0]))
    # convert to all black
    background_mask  = Image.eval(background_mask, lambda px: 1 if px != 0 else 1)
    next_image_x, next_image_y = x_offset, y_offset

    for i,image in tqdm(enumerate(images)):
        image_height, image_width = image.size[1], image.size[0]

        if rotate:
            # Calculate rotated image height
            A = image_height / np.tan(np.deg2rad(abs(rotate_angle)))
            image_height_for_measures = (A + image_width) * np.sin(np.deg2rad(abs(rotate_angle)))
            image_height_for_measures = np.ceil(image_height_for_measures).astype(int)
        else:
            image_height_for_measures = image_height

        random_y = np.random.randint(0, int(image_width / 5))
        
        print(next_image_x, next_image_y)
        if next_image_x + image_height_for_measures >= shape[1]:  
            next_image_x = x_offset + random_y
            next_image_y = y_offset

        if next_image_y + image_width >= shape[0]:
            next_image_x += max_height_by_row + random_y
            next_image_y = y_offset
            max_height_by_row = -1

        remaining_space_x = shape[0] - next_image_x
        remaining_space_y = shape[1] - next_image_y
        # print(remaining_space_x, remaining_space_y)

        if next_image_x >= shape[0] or next_image_y >= shape[1] or remaining_space_x < image_height_for_measures or remaining_space_y < image_width:
            print("No space left")
            break
        
        # increase contrast of image
        image = Image.eval(image, lambda px: px * 8)

        mask = image.convert("L")
        background.paste(image, (next_image_y, next_image_x), mask)

        mask_mask = masks[i].convert("L")

        background_mask.paste(mask_mask, (next_image_y, next_image_x),mask_mask)
        # convert all non zero pixels to 255
        # background_mask = Image.eval(background_mask, lambda px: 255 if px != 0 else 0)

        next_image_y += image_width + random_y
        # next_image_x += image_height_for_measures

        if image_height_for_measures > max_height_by_row:
            max_height_by_row = image_height_for_measures

    background.save("out/sin01.png")
    background_mask.save("out/sin01_mask.png")

text = """කොළඹ - නුවර කාර්යාල සේවකයින් සේවකයින් සේවකයින්"""

main(text.strip(),"background/paper01.jpg","fonts/sin/AbhayaLibre-SemiBold.ttf",50,"#000000")