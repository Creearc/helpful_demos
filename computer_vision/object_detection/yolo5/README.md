## Репозиторий 
https://github.com/ultralytics/yolov5

## Установка Docker
https://www.digitalocean.com/community/tutorials/docker-ubuntu-18-04-1-ru

## Работа с контейнером
https://docs.ultralytics.com/environments/Docker-Quickstart/

## Начало работы
- https://docs.ultralytics.com/quick-start/
- https://docs.ultralytics.com/tutorials/train-custom-datasets/


### Запуск обучения
```
python3 train.py --img 640 --batch 28 --epochs 20 --data ~/datasets/yolo5/cocos/coco_set_4.yaml --weights runs/train/exp15/weights/best.pt
```
