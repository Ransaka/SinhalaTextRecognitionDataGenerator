import json
from pathlib import Path
from generator import generator, randomize_parameters
from multiprocessing import Pool

TEXT = """
ජාත්‍යන්තර පොලීසිය විසින් මේ වනවිට අපරාධකරුවන්ට රතු නිවේදන නිකුත් කිරීම ප්‍රතික්ෂේප කරන බව අපරාධ හා වැඩබලන නීති දිසාව භාර නියෝජ්‍ය පොලිස්පති අසංග කරවිට මහතා පවසයි.
ඔහු පෙන්වා දෙන්නේ, මත්ද්‍රව්‍ය සම්බන්ධ වැරදි සහ ඝාතනවලට අදාළව මෙරටදී ලබාදෙන දඬුවම මරණීය දණ්ඩනය බවට සඳහන්වීම ඊට හේතුව බවය. 
විවෘත සහ වගකිවයුතු රජයක් සඳහා ආංශික අධීක්ෂණ කාරක සභාව හමුවට මහජන ආරක්ෂණ අමාත්‍යංශය හා ශ්‍රී ලංකා පොලීසිය කැඳවු අවස්ථාවේදී මේ පිළිබඳ කරුණු අනාවරණ විය.
"""

class SinhalaTextGenerator:
    def __init__(self) -> None:
        pass
    def generate(self,N,num_procs):
        parameters = randomize_parameters(N)
        parameters['text'] = [TEXT for i in range(N)]
        kwargs = {
            "text":parameters["text"],
            "background_image_path":parameters["background_image_path"],
            "font_filepath":parameters["font_filepath"],
            "font_size":parameters["font_size"],
            "color":parameters["color"],
            "perspective_transform":parameters["perspective_transform"]
        }
        print(kwargs)
        with Pool(num_procs) as p:
            results = p.starmap(generator, zip(*kwargs.values()))
        
        labels = [res[2] for res in results]
        images = [res[0] for res in results]
        masks = [res[1] for res in results]

        self.save_results(labels,images,masks)

    def save_results(self,labels,images,masks):
        Path("out").mkdir(exist_ok=True)
        Path("out/images").mkdir(exist_ok=True)
        Path("out/masks").mkdir(exist_ok=True)
        # Save as json
        with open("out/labels.json","wb") as f:
            f.write(json.dumps(labels,indent=4,ensure_ascii=False).encode("utf-8"))
        # Save as images
        for i in range(len(images)):
            image_id = list(labels[i].keys())[0]
            images[i].save(f"out/images/image_{image_id}.png")
            masks[i].save(f"out/masks/mask_{image_id}.png")

if __name__ == "__main__":
    sinhala_text_generator = SinhalaTextGenerator()
    sinhala_text_generator.generate(N=100,num_procs=8)