import glob
import os
import shutil
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET



def deshuffle_training( data_path ):
    """
    deshuffle the training data provided by KUWC
    uses the path and filename infomration from the annotation files
    """

    # find files
    xml_files = [f for f in glob.glob(data_path + "Annotation/**/*.xml", recursive=True)]


    for xml in xml_files:
        print(xml)
        # get info
        root = ET.parse(xml).getroot()
        filename = root.find('filename').text
        folder = root.find('folder').text
        path = root.find('path').text

        # adenoma is formatted differently
        if ".jpg" in path or ".png" in path or ".bmp" in path:
            dir_name = os.path.dirname(path).replace("/", "-")
        else:
            dir_name = path.replace("/", "-")
        new_name = filename.replace("adenoma_", "").replace(".jpg", "").replace(".png", "").replace(".bmp", "")
        # if "adenoma" in folder:
        #     dir_name = os.path.basename(path)
        #     new_name = filename.replace("adenoma_", "").replace(".jpg", "").replace(".png", "").replace(".bmp", "")
        # else:
        #     dir_name = folder
        #     new_name = filename.replace(".jpg", "").replace(".png", "").replace(".bmp", "")

        # create new dirs if necessary
        xml_dir_path = os.path.join(data_path + "Annotation/", dir_name)
        if not os.path.exists(xml_dir_path):
            os.mkdir(xml_dir_path)
        
        img = xml.replace("Annotation", "Image").replace(".xml", ".jpg")
        img_dir_path = xml_dir_path.replace("Annotation", "Image")
        if not os.path.exists(img_dir_path):
            os.mkdir(img_dir_path)


        # move and rename files
        shutil.move(xml, os.path.join(xml_dir_path, new_name + ".xml"))
        shutil.move(img, os.path.join(img_dir_path, new_name + ".jpg"))




def rename_dirs_to_tr_dirs( data_path):
    """
    rename the dirs created by deshuffle_training() to tr1, tr2, ....
    :param data_path:
    :return:
    """

    annotations_path = os.path.join(data_path, "Annotation")

    # collect video dir names
    xml_dirs = [f.path for f in os.scandir(annotations_path) if f.is_dir()]

    # loop video dirs
    i = 1
    for xml_dir in xml_dirs:
        img_dir = xml_dir.replace("Annotation", "Image")

        print(xml_dir)
        print( os.path.join(os.path.dirname(xml_dir), "tr"+str(i)))

        os.rename(xml_dir, os.path.join(os.path.dirname(xml_dir), "tr"+str(i)))
        os.rename(img_dir, os.path.join(os.path.dirname(img_dir), "tr" + str(i)))

        i += 1


if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    # deshuffle_training("KUMC_PolypsSet/train2019/")
    rename_dirs_to_tr_dirs("KUMC_PolypsSet/train2019/")
    exit(0)