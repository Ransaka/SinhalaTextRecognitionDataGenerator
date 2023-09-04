import json
from pathlib import Path
import numpy as np
from tqdm import tqdm
from .generator import generator, randomize_parameters
from multiprocessing import Pool, cpu_count
import logging

logger = logging.getLogger(__name__)

class SinhalaTextGenerator:
    def __init__(
            self,
            data_path,
            save_interval=100,
            shape=(512, 512),
            min_text_length=1,
            font_dir=None, 
            font_size=None, 
            background_image_dir=None,
            color=None, 
            perspective_transform=None,
            start_word_xy = None,
            line_space = None,
            word_space = None,
            rotate_flag = False,
            sample_with_replace =False
            ) -> None:
        self.text = open(data_path,"r").read().split("\n")
        self.text = [t for t in self.text if len(t) > min_text_length]
        self.save_interval = save_interval
        self.font_dir = font_dir
        self.font_size = font_size
        self.background_image_dir = background_image_dir
        self.color = color
        self.shape = shape
        self.perspective_transform = perspective_transform
        self.start_word_xy = start_word_xy
        self.line_space = line_space
        self.word_space = word_space
        self.rotate_flag = rotate_flag
        self.sample_with_replace = sample_with_replace

    def generate_with_progress(self,args):
        common_args = [self.shape, self.start_word_xy, self.line_space, self.word_space, self.rotate_flag]
        args = list(args)
        args.extend(common_args)
        return generator(*args)
    
    def generate(self, N, num_procs):
        # if requred sample size is greater than the number of text samples in the dataset throw an warning
        if N > len(self.text):
            logger.warning(
                f"Requested sample size ({N}) is greater than the number of text samples ({len(self.text)}). This will result in duplicate samples."
            )
        parameters = randomize_parameters(
            N,
            font_dir=self.font_dir,
            font_size=self.font_size,
            background_image_dir=self.background_image_dir,
            color=self.color,
            perspective_transform=self.perspective_transform
            )
        parameters['text'] = np.random.choice(self.text, N, replace= self.sample_with_replace)
        kwargs = {
            "text": parameters["text"],
            "background_image_path": parameters["background_image_path"],
            "font_filepath": parameters["font_filepath"],
            "font_size": parameters["font_size"],
            "color": parameters["color"],
            "perspective_transform": parameters["perspective_transform"]
        }
        
        if num_procs == -1:
            num_procs = cpu_count()

        with Pool(num_procs) as p:
            results = []
            labels_list = []
            with tqdm(desc="Generating Images", total=N) as progress:
                for i, result in enumerate(p.map(self.generate_with_progress, zip(*kwargs.values()))):
                    results.append(result)
                    progress.update(1)

                    if i % self.save_interval == 0:
                        labels = [res[2] for res in results]
                        images = [res[0] for res in results]
                        masks = [res[1] for res in results]
                        image_ids = [list(label.keys())[0] for label in labels]
                        self.save_images( images, masks, image_ids)

                        labels_list.extend(labels)
                        results = []  # Clear the results list

            # Save any remaining results
            if results:
                labels = [res[2] for res in results]
                images = [res[0] for res in results]
                masks = [res[1] for res in results]
                image_ids = [list(label.keys())[0] for label in labels]

                self.save_images(images, masks, image_ids)
                labels_list.extend(labels)

        self.save_labels(labels_list)

    def save_labels(self,labels):
        with open("../out/labels.json", "w",encoding='utf-8') as f:
            json.dump(labels, f, indent=4, ensure_ascii=False)

    def save_images(self,images,masks,image_ids):
        Path("../out").mkdir(exist_ok=True)
        Path("../out/images").mkdir(exist_ok=True)
        Path("../out/masks").mkdir(exist_ok=True)
        # Save as images
        for i in range(len(images)):
            image_id = image_ids[i]
            images[i].save(f"../out/images/image_{image_id}.png")
            masks[i].save(f"../out/masks/mask_{image_id}.png")