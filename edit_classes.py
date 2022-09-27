import os 
import shutil 


def first_name_of_filename(dfolder_path,fname):
    dir_folder=os.listdir(dfolder_path)
    same_first_names=[]
    for file in dir_folder:
        if file.startswith(str(fname.split('.')[0])):
            same_first_names.append(file)
        else:
            continue
    return len(same_first_names)

def deleting_predefined_classes(class_path):
    with open(class_path,'r+') as f:
        lines=f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines[15:]:
            f.write(line) 
    print("Succes deleting predefined class label")
      
        


def copy_file(fpath,file):
    print("copying classes.txt")
    dfolder_path=str(input("Enter dest folder:"))
    dpath=os.path.join(dfolder_path,file)
    if not os.path.exists(dpath):
        #try copying file to destination folder
        try:
            shutil.copyfile(fpath,dpath)
            print(f"SUCCES:copying {fpath} to {dpath}")
            deleting_predefined_classes(dpath)
        except Exception as e:
            print(f"COPYING ERROR:{e}")
    #make new name file is file already existed
    else:
        n_same=first_name_of_filename(dfolder_path,file)
        dpath=os.path.join(dfolder_path,str(file.split(".")[0])+ "_" + str(n_same) + ".txt")
        try:
            shutil.copyfile(fpath,dpath)
            print(f"SUCCES:copying {fpath} to {dpath}")
            deleting_predefined_classes(dpath)
        except Exception as e:
            print(f"COPYING ERROR:{e}")

def delete_classes_path(folder_path,dir):
    #looping over directory
    for file in dir:
        file_path=os.path.join(folder_path,file)
        #delete filename classes.txt
        if file == 'classes.txt':
            try:
                #copy file to another directory to store label classes that has been saved in classes.txt
                copy_file(file_path,file)
                os.remove(file_path)
                print(f"SUCCES:deleting {file_path}")
            except Exception as e:
                print(f"DELETION ERROR:{e}")
        else:
            continue
    new_dir=os.listdir(folder_path)
    return new_dir

def editing_class_label(folder_path,dir):
    #edit label class annotation in every .txt file
    for file in dir:
        file_path=os.path.join(folder_path,file)
        if file_path.endswith('.txt'):
            with open(file_path,'r+') as f:
                #store every line in file
                lines=f.readlines()
                #clean all content in file
                f.seek(0)
                f.truncate()
                #accessing every text line 
                for line in lines:
                    #text position after class label
                    prev_line=line[3:]
                    #classes position in line
                    prev_label_class=line[0:2]
                    #updated new class label
                    new_label_class=int(prev_label_class)-15
                    #updated content with new labeled class
                    f.write(str(new_label_class)+" "+prev_line)
            print(f"SUCCES:EDIT LABEL CLASSES for {file_path} " )
        else:
            print('not in .txt format')
            continue

def main():
    print("EDITING LABEL CLASSES ANNOTATION YOLO FILE")
    #enter folder directory path
    folder_path=str(input("Enter folder path:"))
    try:
        folder_dir=os.listdir(folder_path)
        size_before=len(folder_dir)
        folder_dir=delete_classes_path(folder_path,folder_dir)
        editing_class_label(folder_path,folder_dir)
        print(f'old size directory:{size_before}')
        print(f"new size directory:{len(folder_dir)}")
    except Exception as e:
        print(f"ERROR:{e}")


if __name__=='__main__':
    main()           
