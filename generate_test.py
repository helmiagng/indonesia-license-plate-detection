import os

image_files = []
os.chdir(os.path.join("/content/darknet/data", "valid_yolo_plate"))
for filename in os.listdir(os.getcwd()):
    if filename.endswith(".jpg"):
        image_files.append("/content/darknet/data/valid_yolo_plate/" + filename)
os.chdir("..")
with open("test.txt", "w") as outfile:
    for image in image_files:
        outfile.write(image)
        outfile.write("\n")
    outfile.close()
os.chdir("..")