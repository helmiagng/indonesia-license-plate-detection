import cv2
import PIL
import os


def delete_non_jpg(imgs_dir_path,imgs):
	for img in imgs:
		delete=False
		file_path=os.path.join(imgs_dir_path,img)
		if not file_path.endswith(".jpg"):
			delete=True
		else:
			continue

		if delete:
			os.remove(file_path)	
			print(f"SUCCES:deleting file {file_path} ")
	return imgs

def check_opencv(img_dir_path,images):
	# loop over the image paths we just downloaded
	for image in images:
		# initialize if the image should be deleted or not
		delete = False

		# try to load the image
		try:
			image = cv2.imread(img_dir_path+ "\\"  + image)

			# if the image is `None` then we could not properly load it
			# from disk, so delete it
			if image is None:
				delete = True
			print(f"success read image")
		# if OpenCV cannot load the image then the image is likely
		# corrupt so we should delete it
		except:
			print("Except")
			delete = True

		# check to see if the image should be deleted
		if delete:
			file_dir=os.path.join(img_dir_path,image)
			os.remove(file_dir)
			print(f"SUCCESS:deleting file {file_dir}")
	return images

def main():
	image_dir_path=str(input("enter path:"))
	images=os.listdir(image_dir_path)
	images=delete_non_jpg(image_dir_path,images)
	images=check_opencv(image_dir_path,images)
	new_size_dir=len(os.listdir(image_dir_path))

	print(f"size before deletion:{len(images)}")
	print(f"new_size after deletion:{new_size_dir}")

if __name__=='__main__':
	main()
