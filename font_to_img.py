from PIL import Image, ImageFont, ImageDraw, ImageColor
import cv2
import numpy as np
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

def text_to_image(
text: str,
font_filepath: str,
font_size: int,
color: (int, int, int), #color is in RGB
font_align="center",
rotate=False):

    font = ImageFont.truetype(font_filepath, size=font_size)
    box = font.getsize_multiline(text)
    img = Image.new("RGBA", (box[0], box[1]))

    #add padding
    img = Image.new("RGBA", (box[0]+int(font_size/4), box[1]+int(font_size/4)))

    # create image mask
    img_mask = Image.new("L", img.size, color='white')

    draw = ImageDraw.Draw(img)
    draw_point = (0, 0)
    draw.multiline_text(draw_point, text, font=font, fill=color, align=font_align,embedded_color=True,stroke_fill = "#282828")
    if rotate:
        img = img.rotate(rotate, expand=True)
        img_mask = img_mask.rotate(rotate, expand=True,resample=Image.BICUBIC)
        rotate_angle = rotate
    else:
        rotate_angle = 0
    return img, img_mask,rotate_angle

def main(text,background_img_path,font_path,font_size,color,shape=(512,512),rotate_flag=True):
    if rotate_flag:
        rotate = np.random.randint(-15,15)
    else:
        rotate = rotate_flag
    images = [text_to_image(
        text=i.replace(" ",""),
        font_filepath=font_path,
        font_size=font_size,
        color=color,
        rotate=rotate
        ) for i in text.split()
        ]
    text_images = [i[0] for i in images]
    masks = [i[1] for i in images]
    
    # combine images
    for image,mask in zip(text_images,masks):
        image.paste(mask, mask=mask)

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
        
        mask = image.convert("L")
        background.paste(image, (next_image_y, next_image_x), mask)

        mask_mask = masks[i].convert("L")
        
        # if mask_mask is transparent then convert to white
        # if np.array(mask_mask).sum() == 0:
        #     mask_mask = Image.new("L", mask_mask.size, color=255)


        background_mask.paste(mask_mask, (next_image_y, next_image_x),mask_mask)

        next_image_y += image_width + random_y
        # next_image_x += image_height_for_measures

        if image_height_for_measures > max_height_by_row:
            max_height_by_row = image_height_for_measures

    background.save("out/sin01.png")
    background_mask.save("out/sin01_mask.png")

text = """කොළඹ - නුවර කාර්යාල සේවකයින් MAMA M"""

main(text.strip(),"background/mink-mingle-96JD67agngE-unsplash.jpg","fonts/sin/AbhayaLibre-Medium.ttf",20,(255, 255, 255))