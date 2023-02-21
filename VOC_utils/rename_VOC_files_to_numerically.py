import glob
import os
import shutil
from pathlib import Path



def rename_VOC_files_to_numerically( data_path ):
    """
    rename all files in numerical order
    so all frames of a video start with frame/file 1.jpg
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
            for img in sorted(vid_dir.glob("*.jpg")):
                anno_file = Path(str(img).replace("Image", "Annotation")).with_suffix(".xml")

                print(img)
                img = img.rename(img.with_stem(str(i)))
                print("renamed to: ", img)

                print(anno_file)
                anno_file = anno_file.rename(anno_file.with_stem(str(i)))
                print("renamed to: ", anno_file)

                i += 1





if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    # remove_files_without_image_or_annotation("KUMC_PolypsSet/")
    rename_VOC_files_to_numerically("processed_data/SUN/Image/")
    exit(0)
