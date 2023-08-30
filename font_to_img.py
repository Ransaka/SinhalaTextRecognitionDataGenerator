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

    add_background(images = text_images,background_image_path = background_img_path,shape = shape,rotate_angle = rotate, rotate=rotate)

def add_background(images, background_image_path, shape, rotate_angle, rotate=True):
    # if rotate == True and len(images) == sum(rotate_angles==0):
    #     raise Exception("ROtate set to True but all images are not rotated")
    # if rotate == False and len(images) != sum(rotate_angles==0):
    #     raise Exception("ROtate set to False but all images are not rotated")
    
    x_offset = y_offset = 100

    # Read background image
    background = cv2.imread(background_image_path)
    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)  # Fix color conversion

    # Resize background image
    background = cv2.resize(background, (shape[1], shape[0]))  # Swap shape dimensions

    # Convert PIL images to RGB images
    images = [np.array(i.convert("RGB")) for i in images]

    # Add images to background
    next_image_x = x_offset
    next_image_y = y_offset
    print("*"*30,rotate_angle,"*"*30)
    max_height_by_row = -1
    for i,image in tqdm(enumerate(images)):
        # save image
        # cv2.imwrite("out/{}.png".format(next_image_x), image)
        image_height, image_width, _ = image.shape
        # print(f"Current max height by row {max_height_by_row}")
        if rotate:
            A = image_height / np.tan(np.deg2rad(abs(rotate_angle)))
            image_height_for_measures = (A + image_width) * np.sin(np.deg2rad(abs(rotate_angle)))
            # round to nearest integer
            image_height_for_measures = np.ceil(image_height_for_measures).astype(int)
        else:
            image_height_for_measures = image_height
        
        if image_height_for_measures > max_height_by_row:
            max_height_by_row = image_height_for_measures

        random_y = 5#np.random.randint(0, int(image_width / 5))

        if image_height_for_measures + next_image_x >= shape[0]:  # Check height condition
            next_image_x = x_offset + random_y
            next_image_y = y_offset

        if image_width + next_image_y >= shape[1]:  # Check width condition
            next_image_x += max_height_by_row + random_y
            next_image_y = y_offset
            max_height_by_row = -1

        remaining_space_x = shape[0] - next_image_x
        remaining_space_y = shape[1] - next_image_y

        if next_image_x >= shape[0] or next_image_y >= shape[1] or remaining_space_x < image_height_for_measures or remaining_space_y < image_width:
            print("No space left")
            break

        background[next_image_x:next_image_x + image_height,
                   next_image_y:next_image_y + image_width] = image

        next_image_y += image_width + random_y
        print(max_height_by_row)

        # print("Remaining space x", )
        # print("Remaining space y", shape[1] - next_image_y)
        # print()

    # Return as PIL image
    background = Image.fromarray(background)

    # Save image
    background.save("out/sin01.png")

text = """කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ.
කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ."""

main(text.strip(),"background/mink-mingle-96JD67agngE-unsplash.jpg","fonts/sin/AbhayaLibre-Medium.ttf",70,(255, 255, 255))