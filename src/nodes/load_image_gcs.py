import logging
import os
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
from ..client import GoogleStorageClient

class LoadImageGCS:

    def __init__(self):
        self.gcs_client = GoogleStorageClient()

    @classmethod
    def INPUT_TYPES(s):
        input_dir = os.getenv("GCS_INPUT_DIR", "")
        input_bucket = os.getenv("GCS_BUCKET", "")
        input_project = os.getenv("GCS_PROJECT", "")
        gcp_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        try:
            logging.info(f"Listing files in GCS bucket: {input_dir}")
            files = GoogleStorageClient().gcs_client.list_files(prefix=input_dir)
        except Exception as e:
            logging.error(f"Error listing files in GCS bucket: {e}")
            files = []
        return {
            "required": {
            "image": (sorted(files), {"image_upload": False}),
            "GCS_INPUT_DIR": (input_dir, {
                "multiline": False,
                "default": input_dir,
                "lazy": True
            }),
            "GCS_BUCKET": (input_bucket, {
                "multiline": False,
                "default": input_bucket,
                "lazy": True
            }),
            "GCS_PROJECT": (input_project, {
                "multiline": False,
                "default": input_project,
                "lazy": True
            }),
            "GOOGLE_APPLICATION_CREDENTIALS": (gcp_credentials, {
                "multiline": False,
                "default": gcp_credentials,
                "lazy": True
            }),
            }
        }

    CATEGORY = "ComfyGCS"
    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    
    def load_image(self, image):
        gcs_path = os.path.join(os.getenv("GCS_INPUT_DIR"), image)
        image_path = self.gcs_client.download_file(gcs_path=gcs_path, local_path=f"input/{image}")
        
        img = Image.open(image_path)
        output_images = []
        output_masks = []
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)