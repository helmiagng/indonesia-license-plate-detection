import os

def check_size_of_directory(dataset_path,annot_path):
    print(f"size of images plate dataset:{len(os.listdir(dataset_path))}")
    print(f"size of images plate annotation:{len(os.listdir(annot_path))}")


image_plate_path="C:/project/license plat detection/plat nomor dataset/train2"
image_annot_plate_path="C:/project/license plat detection/plat nomor dataset/train2_yolo_plate"
images_plate=os.listdir(image_plate_path)
images_plate_name=[filename.split(".")[0] for filename in os.listdir(image_plate_path)]
images_annot_plate=[filename_annot.split(".")[0] for filename_annot in os.listdir(image_annot_plate_path)]
check_size_of_directory(image_plate_path,image_annot_plate_path)
if len(images_plate)==len(images_annot_plate):
    print("size of directory is same")
else:
    for i in range(len(images_plate)):
        delete=False
        if images_plate_name[i] not in images_annot_plate:
            print(f"{images_plate_name[i]} not in annot plate directory")
            delete=True
        if delete==True:
            try:
                file_path=os.path.join(image_plate_path , str(images_plate[i]))
                os.remove(file_path)
                print(f"DELETING SUCCES:{file_path} is deleted")
            except Exception as e:
                print(f"ERROR:{e}")
check_size_of_directory(image_plate_path,image_annot_plate_path)