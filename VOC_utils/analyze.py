import glob
import os
import shutil
from PIL import Image, ExifTags
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import re
import csv

from timeit import default_timer as timer


def list_unique_paths( data_path ):
    """
    find all unique directories given in the "path"-parameter of all xmls
    useful to maybe use the "train"-data from KUMC
    :param data_path: dir with children "Annotation" and "Image"; ex.: "D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019"
    """
    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]

    print("glob done")

    paths = sorted({os.path.dirname(root.find('path').text) for xml in xml_files if (root := ET.parse(xml).getroot())})

    print(paths)


def list__paths_and_files( data_path ):
    """
    find all directories and files given in the "path"-parameter of all xmls
    writes result to a csv in the same dir
    useful to maybe use the "train"-data from KUMC
    :param data_path: dir with children "Annotation" and "Image"; ex.: "D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019"
    """
    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]

    print("glob done")

    start = timer()

    # paths = sorted([(os.path.dirname(root.find('path').text), os.path.basename(root.find('path').text)) for xml in xml_files if (root := ET.parse(xml).getroot())])
    paths = sorted(
        [[root.find('path').text, int(os.path.basename(root.find('filename').text).split(".")[0].replace("adenoma_", ""))] for xml in xml_files if
         (root := ET.parse(xml).getroot())])

    for path in paths:
        if "adenoma" not in path[0]:
            path[0] = os.path.dirname(path[0])

    end = timer()
    print("done:")
    print(end - start)

    print("save csv to: ", os.path.join(data_path, "unique_path_files.csv"))
    with open(os.path.join(data_path, "unique_path_files.csv"), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for path in paths:
            writer.writerow(path)
    print(paths)




def analyze_voc_sizes( data_path ):
    """
    analyze the composition of the various resolutions and polyp sizes based on the xml data found
    :param data_path: dir with children "Annotation" and "Image"; ex.: "D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019"
    :return:
    """

    ############
    # analyze the image resolutions
    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]
    # jpg_files = [f for f in glob.glob(data_path + "/**/*.jpg", recursive=True)]

    print("glob done")

    # count unique image sizes from the xml given width and height
    img_sizes_xml = [(int(root.find('size/width').text), int(root.find('size/height').text)) for xml in xml_files if (root := ET.parse(xml).getroot())]
    # img_sizes_jpg = {Image.open(img).size for img in jpg_files if Image.open(img).size}
    img_sizes = np.array(img_sizes_xml)
    sizes_values, sizes_counts = np.unique(img_sizes, axis=0, return_counts=True)
    print("Image resolutions : count")
    for size in zip(sizes_values, sizes_counts):
        print(size[0], ": ", size[1])




    ############
    # analyze the sequence resolutions
    sequence_sizes = []
    annotations_path = os.path.join(data_path, "Annotation")

    # collect video dir names
    video_labels = [f.path for f in os.scandir(annotations_path) if f.is_dir()]

    # loop video dirs
    for video_dir in video_labels:

        seq_xml_files = [f for f in glob.glob(video_dir + "/**/*.xml", recursive=True)]

        # count unique image sizes from the xml given width and height
        img_sizes_xml = [(int(root.find('size/width').text), int(root.find('size/height').text)) for xml in seq_xml_files if
                         (root := ET.parse(xml).getroot())]
        img_sizes = np.array(img_sizes_xml)
        sizes_values, sizes_counts = np.unique(img_sizes, axis=0, return_counts=True)

        if len(sizes_values) > 1:
            print("Single Sequence has different resolutions!")
            print(video_dir)
            for size in zip(sizes_values, sizes_counts):
                print(size[0], ": ", size[1])
            print()

        sequence_sizes.extend(sizes_values)


    sizes_values, sizes_counts = np.unique(sequence_sizes, axis=0, return_counts=True)
    print("Sequence resolutions : count")
    for size in zip(sizes_values, sizes_counts):
        print(size[0], ": ", size[1])




    ############
    # create hist of polyp sizes based on polyp BB coords given in xmls
    # to many unique sizes to count each exact size, so create histogram
    polyp_sizes_xml = []
    for xml in xml_files:
        root = ET.parse(xml).getroot()
        # frames without polyp have no bndbox, so need to check
        if ET.parse(xml).getroot().find('object/bndbox/xmin') is not None:
            polyp_sizes_xml.append((int(root.find('object/bndbox/xmax').text) - int(
                root.find('object/bndbox/xmin').text), int(root.find('object/bndbox/ymax').text) - int(
                root.find('object/bndbox/ymin').text)))

    polyp_sizes = np.array(polyp_sizes_xml)

    # 1D hist
    _ = plt.hist(polyp_sizes, bins='auto')  # arguments are passed to np.histogram
    plt.title("Polyp sizes in KUMC")
    plt.show()

    # 2D hist
    plt.title("Polyp sizes in KUMC")
    H, xedges, yedges = np.histogram2d(polyp_sizes[:, 0], polyp_sizes[:, 1], bins=50)
    # Histogram does not follow Cartesian convention (see Notes),
    # therefore transpose H for visualization purposes.
    H = H.T
    X, Y = np.meshgrid(xedges, yedges)

    plt.pcolormesh(X, Y, H)
    plt.show()



    print("done")








def list_polyp_labels( data_path ):
    """
    list all used data labels and their count
    :param data_path:
    :return:
    """
    start = timer()
    ############
    # analyze the image label annotations
    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]

    print("glob done")

    # count unique image sizes from the xml given width and height
    # pattern = re.compile(r'<name>(.*)</name>')
    # img_labels_xml = [re.search(pattern, f.read()).group(1) for xml in xml_files if (f := open(xml, 'r'))]
    img_labels_xml = [root.find('object/name').text for xml in xml_files if (root := ET.parse(xml).getroot())]

    print("Polyp labels : count")
    for size in zip(Counter(img_labels_xml).keys(), Counter(img_labels_xml).values()):
        print(size[0], ": ", size[1])

    print()

    end = timer()
    print("done:")
    print(end - start)
    start = timer()


    ############
    # analyze the sequence labels
    sequence_labels = []
    annotations_path = os.path.join(data_path, "Annotation")

    # collect video dir names
    video_labels = [f.path for f in os.scandir(annotations_path) if f.is_dir()]

    # loop video dirs
    for video_dir in video_labels:

        seq_xml_files = [f for f in glob.glob(video_dir + "/**/*.xml", recursive=True)]

        # count unique image sizes from the xml given width and height
        # img_labels_xml = [re.search(pattern, f.read()).group(1) for xml in seq_xml_files if (f := open(xml, 'r'))]
        img_labels_xml = [root.find('object/name').text for xml in seq_xml_files if (root := ET.parse(xml).getroot())]

        if len(Counter(img_labels_xml).keys()) > 1:
            print("Single Sequence has different resolutions!")
            print(video_dir)
            for size in zip(Counter(img_labels_xml).keys(), Counter(img_labels_xml).values()):
                print(size[0], ": ", size[1])
            print()

        sequence_labels.extend(Counter(img_labels_xml).keys())

    print("Sequence resolutions : count")
    for size in zip(Counter(sequence_labels).keys(), Counter(sequence_labels).values()):
        print(size[0], ": ", size[1])

    end = timer()
    print("done:")
    print(end - start)



if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    analyze_voc_sizes("KUMC_PolypsSet/")
    # list_unique_paths("KUMC_PolypsSet/PolypsSet/train2019/Annotation")
    # list__paths_and_files("KUMC_PolypsSet/PolypsSet/train2019/")
    # list_polyp_labels("KUMC_PolypsSet/")
    exit(0)
