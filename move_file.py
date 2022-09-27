import shutil
import os
def main():
    folder_path=str(input("Enter source folder path:"))
    dest_folder=str(input("Enter destination folder path:"))
    folder_dir=os.listdir(folder_path)
    for file in folder_dir:
        src=os.path.join(folder_path,file)
        dest=os.path.join(dest_folder,file)
        try:
            shutil.copyfile(src,dest)
            print(f"SUCCES:{src} copied to {dest}")
        except Exception as e:
            print(f"ERROR:{e}")

if __name__=='__main__':
    print("COPYING FILE IN FOLDER DIRECTORY")
    main()