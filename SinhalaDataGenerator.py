import json
from pathlib import Path
import numpy as np
from tqdm import tqdm
from generator import generator, randomize_parameters
from multiprocessing import Pool, cpu_count

class SinhalaTextGenerator:
    def __init__(self,data_path,save_interval=100) -> None:
        self.text = open(data_path,"r").read().split("\n")
        self.text = [t for t in self.text if len(t) > 0]
        self.save_interval = save_interval
    def generate_with_progress(self,args):
        return generator(*args)
    def generate(self, N, num_procs):
        parameters = randomize_parameters(N)
        parameters['text'] = np.random.choice(self.text, N, replace=True)
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
                for i, result in enumerate(p.imap(self.generate_with_progress, zip(*kwargs.values()))):
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
        with open("out/labels.json", "w",encoding='utf-8') as f:
            json.dump(labels, f, indent=4, ensure_ascii=False)

    def save_images(self,images,masks,image_ids):
        Path("out").mkdir(exist_ok=True)
        Path("out/images").mkdir(exist_ok=True)
        Path("out/masks").mkdir(exist_ok=True)
        # Save as images
        for i in range(len(images)):
            image_id = image_ids[i]
            images[i].save(f"out/images/image_{image_id}.png")
            masks[i].save(f"out/masks/mask_{image_id}.png")

if __name__ == "__main__":
    data_path = "text/data.txt"
    sinhala_text_generator = SinhalaTextGenerator(
        data_path=data_path
    )
    sinhala_text_generator.generate(N=100,num_procs=-1)