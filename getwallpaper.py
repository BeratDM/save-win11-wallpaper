import os
import shutil
import hashlib
from datetime import datetime


def file_hash(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def remove_btemp_main():
    # remove temp file if exists
    if os.path.exists(btemp_main_path):
        print("cleaning temp file in source directory.")
        os.remove(btemp_main_path)


def remove_btemp_wp():
    # remove temp file if exists
    if os.path.exists(btemp_wp_path):
        print("cleaning temp file in destination directory.")
        os.remove(btemp_wp_path)

wp_1 = "X:\\Files\\Wallpapers\\n1\\x\\"
order = input(f"\n1.Copy to current directory\n2.Copy to '{wp_1}'\n3.Specify a path\n")
match order:
    case "1":
        wp_folderpath = f"{os.getcwd()}\\"
    case "2":    
        wp_folderpath = wp_1
    case "3":
        wp_folderpath = f"{input("Enter Path: ")}\\"
        if not os.path.exists(wp_folderpath):
            input("path doesn't seem to exist.")
            exit()
            
print(os.getenv('APPDATA'))
main_path = f"{os.getenv('APPDATA')}\\Microsoft\\Windows\\Themes"

btemp_name = "TranscodedWallpaper-BeratTemp"
btemp_main_path = os.path.join(main_path, btemp_name)
btemp_wp_path = os.path.join(wp_folderpath, btemp_name)
remove_btemp_main()

# remove temp file if exists
if os.path.exists(btemp_main_path):
    print("removing duplicate temp file.")
    os.remove(btemp_main_path)
    
shutil.copy(os.path.join(main_path, "TranscodedWallpaper"), btemp_main_path)

# Get hash of current wallpaper
src_hash = file_hash(btemp_main_path)

# Check if same image already exists
for file in os.listdir(wp_folderpath):
    if file.startswith("wp-") and file.endswith(".png"):
        existing_path = os.path.join(wp_folderpath, file)
        if file_hash(existing_path) == src_hash:
            print(f"\nImage already exists as: {file}")
            remove_btemp_wp()  # Clean up temp duplicate
            input("\n")
            exit()

remove_btemp_wp()
shutil.move(btemp_main_path, wp_folderpath)
remove_btemp_main()

now = datetime.now()
datestr = now.strftime("%y-%m-%d-%f")
new_file_name = f"{wp_folderpath}wp-{datestr}.png"
try:
    os.rename(f"{wp_folderpath}{btemp_name}", new_file_name)
except Exception as e:
    print(e)
    if e == "FileExistsError":
        os.rename(f"{wp_folderpath}{btemp_name}d", new_file_name)
        
input(f"process complete. new file: {new_file_name}\n")
