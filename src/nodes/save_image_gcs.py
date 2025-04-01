import os
import json
import tempfile
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from ..client import GoogleStorageClient

class SaveImageGCS:

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.temp_dir = os.path.join(base_dir, "temp/")
        self.gcs_output_dir = os.getenv("GCS_OUTPUT_DIR")
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
                "required": {
                "images": ("IMAGE", ),
                "filename_prefix": ("STRING", {"default": "Image"})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO" },
                }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("gcs_image_paths",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "ComfyGCS"

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = GoogleStorageClient().get_save_path(filename_prefix, images[0].shape[1], images[0].shape[0])
        results = list()
        gcs_image_paths = list()
        
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))            
            file = f"{filename}_{counter:05}_.png"
            temp_file = None
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_file_path = temp_file.name
                    
                    # Save the image to the temporary file
                    img.save(temp_file_path, compress_level=self.compress_level)

                    # Upload the temporary file to GCS
                    gcs_path = os.path.join(full_output_folder, file)
                    file_path = GoogleStorageClient().upload_file(temp_file_path, gcs_path)

                    # Add the GCS path to the GCS_image_paths list
                    gcs_image_paths.append(file_path)
                    
                    # Add the result to the results list
                    results.append({
                        "filename": file,
                        "subfolder": subfolder,
                        "type": self.type
                    })
                    counter += 1

            finally:
                # Delete the temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return { "ui": { "images": results },  "result": (gcs_image_paths,) }