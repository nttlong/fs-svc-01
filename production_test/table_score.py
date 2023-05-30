from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import requests
f=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.png"
f2=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.jpg"
from PIL import Image
im1 = Image.open(f)
im1.save(f2)
image = Image.open(f2)

processor = DetrImageProcessor.from_pretrained("TahaDouaji/detr-doc-table-detection")
model = DetrForObjectDetection.from_pretrained("TahaDouaji/detr-doc-table-detection")

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# convert outputs (bounding boxes and class logits) to COCO API
# let's only keep detections with score > 0.9
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
    )