
import cv2
import PIL
import os

image_dir_path=str(input("enter path:"))
images=os.listdir(image_dir_path)
print(f"size before deletion:{len(images)}")
# loop over the image paths we just downloaded
for imagePath in images:
	# initialize if the image should be deleted or not
	delete = False

	# try to load the image
	try:
		image = cv2.imread(image_dir_path+ "/"  + imagePath)

		# if the image is `None` then we could not properly load it
		# from disk, so delete it
		if image is None:
			delete = True
		print("succes read image")
	# if OpenCV cannot load the image then the image is likely
	# corrupt so we should delete it
	except:
		print("Except")
		delete = True

	# check to see if the image should be deleted
	if delete:
		print("[INFO] deleting {}".format(imagePath))
		file_dir=os.path.join(image_dir_path,imagePath)
		os.remove(file_dir)

new_size_dir=len(os.listdir(image_dir_path))
print(f"new_size after deletion:{new_size_dir}")


