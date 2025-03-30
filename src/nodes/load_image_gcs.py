import logging
import os
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
from ..client import GoogleStorageClient

class LoadImageGCS:

    @classmethod
    def INPUT_TYPES(s):
        input_dir = os.getenv("GCS_INPUT_DIR", "")
        input_bucket = os.getenv("GCS_BUCKET", "")
        input_project = os.getenv("GCS_PROJECT", "")
        gcp_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        return {
            "required": {
                "gcs_input_prefix": ("STRING", { "multiline": False,"default": input_dir }),
                "gcs_bucket": ("STRING", { "multiline": False,"default": input_bucket }),
                "gcs_project": ("STRING", { "multiline": False, "default": input_project }),
            },
            "optional": {
                "google_application_credentials": ("STRING", { "multiline": False, "default": gcp_credentials }),
            },
        }
    
    CATEGORY = "ComfyGCS"
    RETURN_TYPES = ("IMAGE", )
    FUNCTION = "load_image"
    
    def load_image(self, gcs_input_prefix, gcs_bucket, gcs_project, google_application_credentials):
        
        client = GoogleStorageClient(bucket_name=gcs_bucket, project=gcs_project, credentials_sa=google_application_credentials)
        files = client.list_files(prefix=gcs_input_prefix)
        if not files:
            raise ValueError(f"No files found in the specified GCS path: {gcs_input_prefix}")
        
        file = files[0]
        image = os.path.basename(file)
        logging.info(f"Loading image: {image}")
        image_path = client.download_file( gcs_path=image, local_path=f"input/{image}")
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