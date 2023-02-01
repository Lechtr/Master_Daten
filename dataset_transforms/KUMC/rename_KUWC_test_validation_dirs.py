import glob
import os
import shutil
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


def add_prefix_to_dirs( data_path, prefix="t" ):
    """
    rename the dirs created by deshuffle_training() to tr1, tr2, ....
    :param prefix:
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
        print( os.path.join(os.path.dirname(xml_dir), prefix+os.path.basename(xml_dir)))

        os.rename(xml_dir, os.path.join(os.path.dirname(xml_dir), prefix+os.path.basename(xml_dir)))
        os.rename(img_dir, os.path.join(os.path.dirname(img_dir), prefix+os.path.basename(img_dir)))

        i += 1


if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    add_prefix_to_dirs("KUMC_PolypsSet/test2019/", "t")
    add_prefix_to_dirs("KUMC_PolypsSet/val2019/", "v")
    exit(0)