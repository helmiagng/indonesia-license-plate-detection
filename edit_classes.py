import os 

def main():
    folder_path=str(input("Enter folder path:"))
    folder_dir=os.listdir(folder_path)

    classes_path=os.path.join(folder_path,'classes.txt')
    if os.path.exists(classes_path):
        os.remove(classes_path)

    for file in folder_dir:
        file_path=os.path.join(folder_path,file)
        if file_path.endswith('.txt'):
            with open(file_path,'r+') as f:
                lines=f.readlines()
                
                f.seek(0)
                f.truncate()
                for line in lines:
                    prev_line=line[3:]
                    prev_label_class=line[0:2]
                    new_label_class=int(prev_label_class)-15
                    f.write(str(new_label_class)+" "+prev_line)
                
                f.close()
                print(f"EDIT LABEL CLASSES for {file_path} " )
        else:
            print('not in .txt format')
            continue

if __name__=='__main__':
    main()           