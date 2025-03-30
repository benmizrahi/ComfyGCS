from .nodes.load_image_gcs import LoadImageGCS
from .nodes.save_image_gcs import SaveImageGCS


NODE_CLASS_MAPPINGS = {
    "LoadImageGCS": LoadImageGCS,
    "SaveImageGCS": SaveImageGCS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageGCS": "Load Image from GCS",
    "SaveImageGCS": "Save Image to GCS",
}