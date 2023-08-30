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
        rotate_angle = np.random.randint(-20,20)
        img = img.rotate(rotate_angle, expand=True)
        img_mask = img_mask.rotate(rotate_angle, expand=True,resample=Image.BICUBIC)
    return img, img_mask,rotate_angle

def main(text,background_img_path,font_path,font_size,color,shape=(512,512)):
    images = [text_to_image(
        text=i.replace(" ",""),
        font_filepath=font_path,
        font_size=font_size,
        color=color,
        rotate=True
        ) for i in text.split()
        ]
    text_images = [i[0] for i in images]
    masks = [i[1] for i in images]
    rotate_angles = [i[2] for i in images]
    
    # combine images
    for image,mask in zip(text_images,masks):
        image.paste(mask, mask=mask)

    add_background(text_images,background_img_path,shape)

def add_background(images, background_image_path, shape):
    x_offset = y_offset = 20

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

    for image in tqdm(images):
        # save image
        cv2.imwrite("out/{}.png".format(next_image_x), image)
        image_height, image_width, _ = image.shape
        random_y = np.random.randint(0, int(image_width / 5))

        if image_height + next_image_x >= shape[0]:  # Check height condition
            next_image_x = x_offset + random_y
            next_image_y = y_offset

        if image_width + next_image_y >= shape[1]:  # Check width condition
            next_image_x += image_height + random_y
            next_image_y = y_offset

        remaining_space_x = shape[0] - next_image_x
        remaining_space_y = shape[1] - next_image_y

        if next_image_x >= shape[0] or next_image_y >= shape[1] or remaining_space_x < image_height or remaining_space_y < image_width:
            print("No space left")
            break

        background[next_image_x:next_image_x + image_height,
                   next_image_y:next_image_y + image_width] = image

        next_image_y += image_width + random_y


        # print("Remaining space x", )
        # print("Remaining space y", shape[1] - next_image_y)
        # print()

    # Return as PIL image
    background = Image.fromarray(background)

    # Save image
    background.save("out/sin01.png")

text = """කොළඹ - නුවර කාර්යාල සේවකයින් රැගත් බස් රථයක් ලංගම බස්රථයක මුහුණට මුහුණ ගැටී අනතුරක් සිදුව තිබේ."""
main(text.strip(),"background/mink-mingle-96JD67agngE-unsplash.jpg","fonts/sin/AbhayaLibre-Medium.ttf",50,(255, 255, 255))