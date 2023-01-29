import glob
import os
import shutil
from PIL import Image, ExifTags
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt



def remove_files_without_image_or_annotation( data_path ):
    """
    removes all image files or annotation files that do not have a correspondent partner
    :param data_path: dir with children "Annotation" and "Image"; ex.: "D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019"
    """

    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]
    image_files = [f for f in glob.glob(data_path + "/**/*.jpg", recursive=True)]
    image_files.extend([f for f in glob.glob(data_path + "/**/*.png", recursive=True)])
    print("glob done")

    for xml in xml_files:
        jpg_path = xml.replace("Annotation", "Image").replace(".xml", ".jpg")
        png_path = xml.replace("Annotation", "Image").replace(".xml", ".png")

        if not os.path.isfile(jpg_path) and not os.path.isfile(png_path):
            print("remove: ", xml)
            # os.remove(xml)

    print("checking xmls done")

    for img in image_files:
        xml_path = img.replace("Image", "Annotation").replace(".jpg", ".xml").replace(".png", ".xml")

        if not os.path.isfile(xml_path):
            print("remove: ", img)
            # os.remove(img)

    print("checking images done")




def remove_files_without_polyp( data_path ):
    """
    removes all annotation and image files that do not have a polyp
    :param data_path:
    :return:
    """

    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]

    xml_without_polyps = [xml for xml in xml_files if (ET.parse(xml).getroot().find('object') is None)]

    for xml in xml_without_polyps:
        jpg_path = xml.replace("Annotation", "Image").replace(".xml", ".jpg")
        png_path = xml.replace("Annotation", "Image").replace(".xml", ".png")



        if os.path.isfile(jpg_path):
            print("remove: ", xml)
            print("remove: ", jpg_path)
            os.remove(xml)
            os.remove(jpg_path)

        elif os.path.isfile(png_path):
            print("remove: ", xml)
            print("remove: ", png_path)
            os.remove(xml)
            os.remove(png_path)





if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    # remove_files_without_image_or_annotation("KUMC/")
    remove_files_without_polyp("KUMC/")
    exit(0)
