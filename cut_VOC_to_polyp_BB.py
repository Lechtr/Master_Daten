import os
import shutil
from PIL import Image, ExifTags
from pathlib import Path
import xml.etree.ElementTree as ET


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




if __name__ == '__main__':
    cut_voc_to_bb(data_path="D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet\\val2019",
                  dest_path="D:\\Master_Daten\\KUMC_PolypsSet\\PolypsSet_cut\\val2019")
    exit(0)
