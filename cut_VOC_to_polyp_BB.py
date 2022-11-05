import glob
import os
import shutil
from PIL import Image, ExifTags
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

''' Cutting VOC-Detection datasets to the polyps, so no Background is left
reads voc annotation files and cuts the images according to the bounding boxes

ignores folder, filename and path tag of VOC annotations, since they contain false info

Assumes:
    - only one polyp per frame and annotation file
    - in data_path file structure is:
            |-Annotation
                |-1             # folder contain the video sequences
                    |-1.xml     # single frame annotations in VOC format
                    |-2.xml
                    ....
                |-2
                    |-1.xml
                    |-2.xml
                    ....
                |-3
                    |-1.xml
                    |-2.xml
                    ....
                ...
              
            |-Image
                |-1
                    |-1.jpg
                    |-2.jpg
                    ....
                |-2
                    |-1.jpg
                    |-2.jpg
                    ....
                |-3
                    |-1.jpg
                    |-2.jpg
                    ....
                ...

'''



def cut_voc_to_bb( data_path, dest_path ):
    # create destination dir
    Path(dest_path).mkdir(parents=True, exist_ok=True)

    annotations_path = os.path.join(data_path, "Annotation")
    images_path = os.path.join(data_path, "Image")

    # collect video dir names
    video_labels = [f.path for f in os.scandir(annotations_path) if f.is_dir()]

    # loop video dirs
    for video_dir in video_labels:

        # loop through each annotation file/frame of this dir
        annotation_files = [f.path for f in os.scandir(video_dir) if f.is_file()]
        for annotation_file in annotation_files:

            # check for multiple BBs or if no BB
            no_bb = False
            with open(annotation_file) as f:
                lines = f.readlines()
                number_bb_tags = len([line for line in lines if"bndbox" in line])

                if number_bb_tags == 0:
                    no_bb = True
                elif number_bb_tags != 2:
                    print("WARNING: multiple bounding boxes in:", annotation_file)
                    print("this situation is not handled")
                    print("number_bb_tags:", number_bb_tags)

            # skip files with no polyp
            if no_bb:
                continue

            # get BB coordinates
            root = ET.parse(annotation_file).getroot()
            xmin = int(root.find('object/bndbox/xmin').text)
            ymin = int(root.find('object/bndbox/ymin').text)
            xmax = int(root.find('object/bndbox/xmax').text)
            ymax = int(root.find('object/bndbox/ymax').text)

            # get corresponding image
            image_file = Path(annotation_file.replace(annotations_path, images_path).replace(".xml", ".jpg"))
            if not image_file.is_file():
                print("Image file is missing:", image_file)
                continue
            image = Image.open(image_file)

            # get dest path for this image
            index = image_file.parts.index('Image')
            image_dest_path = Path(dest_path).joinpath(*image_file.parts[index:])
            # create path
            Path(image_dest_path.parent).mkdir(parents=True, exist_ok=True)



            # cut image and save
            crop_img = image.crop((xmin, ymin, xmax, ymax))
            crop_img.save(image_dest_path)

    print("done with images")

    # copy whole annotations unchanged
    annotations_path = Path(annotations_path)
    index = annotations_path.parts.index('Annotation')
    annotations_dest_path = Path(dest_path).joinpath(*annotations_path.parts[index:])
    shutil.copytree(annotations_path, annotations_dest_path)
    print("copied annotations")




# find all unique directory given in the "path"-parameter of all xmls
# useful to maybe use the "train"-data from KUMC
def get_unique_paths( data_path):
    xml_files = [f for f in glob.glob(data_path + "/**/*.xml", recursive=True)]

    print("glob done")

    paths = sorted({os.path.dirname(root.find('path').text) for xml in xml_files if (root := ET.parse(xml).getroot())})

    print(paths)



# analyze the composition of the various resolutions and polyp sizes based on the xml data found
def analyze_voc_sizes( data_path ):

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
    plt.title("Polyp sizes")
    plt.show()

    # 2D hist
    plt.title("Polyp sizes")
    H, xedges, yedges = np.histogram2d(polyp_sizes[:, 0], polyp_sizes[:, 1], bins=50)
    # Histogram does not follow Cartesian convention (see Notes),
    # therefore transpose H for visualization purposes.
    H = H.T
    X, Y = np.meshgrid(xedges, yedges)

    plt.pcolormesh(X, Y, H)
    plt.show()



    print("done")





if __name__ == '__main__':
    # cut_voc_to_bb(data_path="D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019",
    #               dest_path="D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet_cut\\val2019")

    analyze_voc_sizes("D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019")
    # get_unique_paths("KUMC_PolypsSet/PolypsSet/train2019")
    exit(0)
