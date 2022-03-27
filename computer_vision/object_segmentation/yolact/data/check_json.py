import json

with open(r'D:/Repos/segmentation/yolact-master/data/cig_butts/val/coco_annotations.json', 'r') as f:
    json_data = json.load(f)
    
print(json.dumps(json_data, indent=2))