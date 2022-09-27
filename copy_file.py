import shutil
import os

def copyfile_to_dest_folder(fpath,dpath,dir):
    for file in dir:
        src=os.path.join(fpath,file)
        dest=os.path.join(dpath,file)
        try:
            if not os.path.exists(dest):
                shutil.copyfile(src,dest)
                print(f"SUCCES:{src} copied to {dest}")
            else:
                print(f"{dest} is exist")
        except Exception as e:
            print(f"ERROR:{e}")

def main():
    folder_path=str(input("Enter source folder path:"))
    dest_folder=str(input("Enter destination folder path:"))
    folder_dir=os.listdir(folder_path)
    copyfile_to_dest_folder(folder_path,dest_folder,folder_dir)

    print(f"destination size directory before coying file: {len(os.listdir(dest_folder))}")
    print(f"destination size directory after coying file: {len(os.listdir(dest_folder))}")

if __name__=='__main__':
    print("COPYING FILE IN FOLDER DIRECTORY")
    main()
