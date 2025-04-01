from src.nodes.load_image_gcs import LoadImageGCS
from src.nodes.save_image_gcs import SaveImageGCS


def test_load_image_gcs():
    loader = LoadImageGCS()
    load = loader.load_image("input-catalog/jerusalem_86140-copy.jpg","comfyui-test","comfyui-project",None)
    assert load is not None


def test_save_image_gcs():
    saver = SaveImageGCS()
    save = saver.save_images(["input/86140.jpg"],"comfyui-test","comfyui-project",None)
    assert save is not None