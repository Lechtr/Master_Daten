import glob
import os
import shutil
from pathlib import Path



def rename_VOC_files_to_numerically( data_path, sort_numerical=False):
    """
    rename all files in numerical order
    so all frames of a video start with frame/file 1.jpg
    :param sort_numerical: if false sorts filenames by default alphabetically, so 1,11,12,13...,2,21,22,....
    if true assumes that the filenames are ints and sorts numerically, so 1,2,3,4,....
    :param data_path:
    :return:
    """

    # iter through all subdirs
    for vid_dir in Path(data_path).iterdir():
        if vid_dir.is_dir():
            print()
            print(vid_dir)
            i = 1

            # iter through files in vid
            if sort_numerical:
                img_files = sorted(vid_dir.glob("*.jpg"), key=lambda file: int(file.stem))
            else:
                img_files = sorted(vid_dir.glob("*.jpg"))

            for img in img_files:
                anno_file = Path(str(img).replace("Image", "Annotation")).with_suffix(".xml")

                # print(img)
                img = img.rename(img.with_stem(str(i)))
                print(img, " renamed to: ", img.with_stem(str(i)))

                # print(anno_file)
                anno_file = anno_file.rename(anno_file.with_stem(str(i)))
                # print("renamed to: ", anno_file)

                i += 1





if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    # rename_VOC_files_to_numerically("processed_data/SUN/Image/", sort_numerical=False)
    rename_VOC_files_to_numerically("processed_data/KUMC/Image", sort_numerical=True)
    exit(0)
