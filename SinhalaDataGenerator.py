from generator import generator, randomize_parameters
from multiprocessing import Pool

TEXT = "කොළඹ - නුවර කාර්යාල සේවකයින් සේවකයින් සේවකයින්"

class SinhalaTextGenerator:
    def __init__(self) -> None:
        pass
    def generate(N,num_procs):
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
        return results

if __name__ == "__main__":
    SinhalaTextGenerator.generate(10,4)