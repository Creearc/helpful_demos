import json

with open(r'D:/hackathon/WildHack/coco_dataset_creator/pycococreator-master/examples/shapes/train/instances_shape_train2018.json', 'r') as f:
    json_data = json.load(f)
    
print(json.dumps(json_data, indent=2))