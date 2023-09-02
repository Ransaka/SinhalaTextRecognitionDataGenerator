from pathlib import Path
from typing import List, Tuple, Union
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps, ImageFilter
import cv2
import numpy as np
from tqdm import tqdm
import warnings
import random
from uuid import uuid4

warnings.filterwarnings("ignore")

def postprocess_image(img:Image,color:str,perspective_transform:bool,blur_radius=0.5):
    # convert all non zero pixels to 255
    img = Image.eval(img, lambda px: 255 if px != 0 else 0)
    # blur the image
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # concert to L mode
    img = img.convert("L")
    # convert to RGBA
    img = ImageOps.colorize(img,black="black", white=color)
    if perspective_transform:
        img = perspective_transformation(img)
    return img
    # return perspective_transform(img)

def perspective_transformation(image:Image):
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
    fonts = list(Path("fonts/sin").glob("*.ttf"))
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
    perspective_transform: bool,
    mask_background_color: Union[str, tuple] = "#FFFFFF",
    color: Union[str, tuple] = "#000000",
    font_align="center",
    rotate=1):

    font = ImageFont.truetype(str(font_filepath), size=font_size)
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
    #     rotate_angle = rotate
    # else:
    #     rotate_angle = 0
    img = postprocess_image(img, blur_radius=0.5, color=color,perspective_transform=perspective_transform)
    return img, img_mask,text

def get_lables_json(text:str,height:int,width:int,x_corrdinate:int,y_corrdinate:int,font_size:int):
    """Write the labels to a json file
    Args:
        text (str): text to be written
        image (Image): image
        x_corrdinate (int): upper left x coordinate
        y_corrdinate (int): upper left y coordinate
        font_size (int): font size
        """
    return {
        "text":text,
        "x":x_corrdinate,
        "y":y_corrdinate,
        "width":width,
        "height":height,
        "font_size":font_size
    }

def generator(text,background_image_path,font_filepath,font_size,color,perspective_transform,shape=(512,512),rotate_flag=False):
    color = color
    mask_background_color =  "white"
    if rotate_flag:
        rotate = np.random.randint(-15,15)
    else:
        rotate = rotate_flag
        
    results = [text_to_image(
        text=i.replace(" ",""),
        font_filepath=font_filepath,
        font_size=font_size,
        mask_background_color=mask_background_color,
        color=color,
        rotate=rotate,
        perspective_transform=perspective_transform
        ) for i in text.split()
        ]
    text_images = [i[0] for i in results]
    masks = [i[1] for i in results]
    text = [i[2] for i in results]
    
    return add_background(
        images = text_images, 
        text=text, 
        background_image_path = background_image_path, 
        shape = shape, 
        rotate_angle = rotate, 
        masks=masks, 
        rotate=rotate,
        font_size=font_size
        )

def add_background(
        images:Image, 
        background_image_path:Path, 
        shape:Tuple, 
        rotate_angle:int,
        masks:List, 
        text:List, 
        font_size:int,
        rotate=True):
    x_offset, y_offset = 10, 10
    max_height_by_row = -1

    # Read background image
    background = cv2.imread(str(background_image_path))
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
    image_id = str(uuid4())
    labels = {image_id:[]}
    for i,image in enumerate(images):
        image_height, image_width = image.size[1], image.size[0]

        if rotate:
            # Calculate rotated image height
            A = image_height / np.tan(np.deg2rad(abs(rotate_angle)))
            image_height_for_measures = (A + image_width) * np.sin(np.deg2rad(abs(rotate_angle)))
            image_height_for_measures = np.ceil(image_height_for_measures).astype(int)
        else:
            image_height_for_measures = image_height

        random_y = np.random.randint(0, int(image_width / 5))
        
        # print(next_image_x, next_image_y)
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
            # print("No space left")
            break
        
        # increase contrast of image
        image = Image.eval(image, lambda px: px * 8)

        mask = image.convert("L")
        background.paste(image, (next_image_y, next_image_x), mask)

        mask_mask = masks[i].convert("L")

        background_mask.paste(mask_mask, (next_image_y, next_image_x),mask_mask)
        labels[image_id].append(get_lables_json(text=text[i],height=image_height_for_measures,width=image_width,x_corrdinate=next_image_y,y_corrdinate=next_image_x,font_size=font_size))
        # convert all non zero pixels to 255
        # background_mask = Image.eval(background_mask, lambda px: 255 if px != 0 else 0)

        next_image_y += image_width + random_y
        # next_image_x += image_height_for_measures

        if image_height_for_measures > max_height_by_row:
            max_height_by_row = image_height_for_measures

    # background.save(f"out/{image_id}.png")
    # background_mask.save(f"out/{image_id}_mask.png")
    return background,background_mask,labels