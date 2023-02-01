import os
import re
from PIL import Image

'''Transform SUN dataset to Pascal VOC Format'''



folder_holding_annotation_files = "D:\\Master_Daten\\sundatabase_positive\\annotation_txt" # input("Enter the path to the yolo files: ").replace("'", "").strip()
image_folder = "D:\\Master_Daten\\sundatabase_positive"
yolo_class_list_file = "D:\\Master_Daten\\sundatabase_yolo_split\\classes.txt" # input("Enter the path to the file that has the yolo classes (typically classes.txt): ").strip()
classification_labels = "D:\\Master_Daten\\sunddatabase_stft\\diag_classes.txt"

# Get a list of all the classes used in the yolo format
with open(yolo_class_list_file) as f:
    yolo_classes = f.readlines()
array_of_yolo_classes = [x.strip() for x in yolo_classes]

with open(classification_labels) as f:
    adenoma_classes = f.readlines()

array_of_adenoma_classes = [x.split(",")[2].strip() for x in adenoma_classes]



# Description of SUN Format values
# case_M_20181001100941_0U62372100109341_1_005_001-1_a10_ayy_image0001.jpg 408,545,568,722,0
# file_name min_X min_Y max_X max_Y class

def is_number( n ):
    try:
        float(n)
        return True
    except ValueError:
        return False


def translate_classes_to_adenoma_vs_non_adenoma(name):
    if name == "Low-grade adenoma":
        return 0
    elif name == "High-grade adenoma":
        return 0
    elif name == "Traditional serrated adenoma":
        return 0
    elif name == "Invasive cancer (T1b)" or name == "Invasive cancer":
        return 0
    elif name == "Sessile serrated lesion":
        return 1
    elif name == "Hyperplastic polyp":
        return 1
    else:
        print("ERROR: class not known")
        return -1



array_of_adenoma_classes_numerical = [translate_classes_to_adenoma_vs_non_adenoma(x) for x in array_of_adenoma_classes]

os.chdir(folder_holding_annotation_files)

xml_path = folder_holding_annotation_files + os.sep + 'XML'
if not os.path.exists(xml_path):
    # If an XML folder does not already exist, make one
    os.mkdir(xml_path)


for case_file in os.listdir(folder_holding_annotation_files):
    if case_file.endswith("txt"):

        print(case_file)

        the_file = open(case_file, 'r')
        all_lines = the_file.readlines()
        case_name = os.path.basename(case_file).split('.')[0]
        case_number = int(case_name.split("case")[1])

        # create new case subdir
        case_path = os.path.join(xml_path, case_name)
        if not os.path.exists(case_path):
            # If a case folder does not already exist, make one
            os.mkdir(case_path)



        for row_index, row in enumerate(all_lines):
            # Start the XML file
            image_name = row.split()[0]
            orig_img = Image.open(
                os.path.join(image_folder, case_name, image_name))  # open the image

            image_width = orig_img.width
            image_height = orig_img.height


            with open(os.path.join(case_path, case_name+"-"+str(row_index+1)+".xml"), 'w') as f: # image_name.replace(".jpg", ".xml")), 'w') as f:

                bbox_info = row.split()[1].split(',')
                bbox_coord = bbox_info[0:4]
                bbox_class = bbox_info[4]

                f.write('<annotation>\n')
                f.write('\t<folder>train</folder>\n')
                f.write('\t<filename>' + row.split()[0] + '</filename>\n')
                #f.write('\t<path>' + os.getcwd() + os.sep + image_name + '</path>\n')
                f.write('\t<source>\n')
                f.write('\t\t<database>SUN</database>\n')
                f.write('\t</source>\n')
                f.write('\t<size>\n')
                f.write('\t\t<width>' + str(image_width) + '</width>\n')
                f.write('\t\t<height>' + str(image_height) + '</height>\n')
                f.write('\t\t<depth>3</depth>\n')  # assuming a 3 channel color image (RGB)
                f.write('\t</size>\n')
                # f.write('\t<segmented>0</segmented>\n')

                # initalize the variables
                class_number = int(bbox_class)
                x_min = bbox_info[0]
                y_min = bbox_info[1]
                x_max = bbox_info[2]
                y_max = bbox_info[3]


                # # assign the variables
                # object_name = array_of_yolo_classes[class_number]
                # if class_number == 0:
                #     positive = "1"
                # else:
                #     positive = "0"

                # assign adenoma vs non-adenoma classes
                positive = str(array_of_adenoma_classes_numerical[case_number-1])
                object_name = array_of_adenoma_classes[case_number-1]


                # write each object to the file
                f.write('\t<object>\n')
                f.write('\t\t<name>' + object_name + '</name>\n')
                # f.write('\t\t<pose>Unspecified</pose>\n')
                # f.write('\t\t<truncated>0</truncated>\n')
                # f.write('\t\t<difficult>0</difficult>\n')
                f.write('\t\t<positive>' + positive + '</positive>\n')
                f.write('\t\t<bndbox>\n')
                f.write('\t\t\t<xmin>' + x_min + '</xmin>\n')
                f.write('\t\t\t<ymin>' + y_min + '</ymin>\n')
                f.write('\t\t\t<xmax>' + x_max + '</xmax>\n')
                f.write('\t\t\t<ymax>' + y_max + '</ymax>\n')
                f.write('\t\t</bndbox>\n')
                f.write('\t</object>\n')

                # Close the annotation tag once all the objects have been written to the file
                f.write('</annotation>\n')
                f.close()  # Close the file

# Check to make sure the sprite file is now in the folder
if os.path.exists("XML"):
    print("Conversion complete")
else:
    print("There was a problem converting the files")