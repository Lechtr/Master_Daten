import os
import shutil
import numpy as np
from PIL import Image, ExifTags
from pathlib import Path

""" this code is used to transform the SUN-Dataset found here: http://amed8k.sundatabase.org/
    into the yolo-format
    author: Joshua Friedrich
"""


''' utility functions'''
# Get orientation exif tag
for orientation in ExifTags.TAGS.keys():
    if ExifTags.TAGS[orientation] == 'Orientation':
        break

def exif_size(img):
    # Returns exif-corrected PIL size
    s = img.size  # (width, height)
    try:
        rotation = dict(img._getexif().items())[orientation]
        if rotation == 6:  # rotation 270
            s = (s[1], s[0])
        elif rotation == 8:  # rotation 90
            s = (s[1], s[0])
    except:
        pass

    return s

# replace last occurrence of given substring
def rreplace(s, old, new, occurrence=1):
    li = s.rsplit(old, occurrence)
    return new.join(li)




''' Transform Dataset into yolo-format'''
"""
assumes:
    - Parameters:
        dir_positive      = directory with the positive images of SUN; images are still in the cases-subdirs, ex. {dir_positive}//case1//
        dir_negative      = directory with the negative images of SUN; images are still in the cases-subdirs, ex. {dir_negative}//case1//
        destination_dir   = target directory, where to save the new resized images & labels
does:
    - resizes images to 640px height
    - transform labels to yolo-format => each frame one txt file & normalized BBox-coordinates
    - saves them in destination_dir in a negative & positive subdir, keeping the case-subdir-structure
        - creates these dirs if necessary

    - DELETES existing {destination_dir}//positive & {destination_dir}//negative dirs with all contents
"""

def resize_images_and_transform_labels(dir_positive = "D:\\Master_Daten\\sundatabase_positive\\",
                                       dir_negative = "D:\\Master_Daten\\sundatabase_negative\\",
                                       destination_dir="D:\\Master_Daten\\sundatabase_resized_normalized\\",
                                       ):

    # directory that holds the labels
    dir_label = os.path.join(dir_positive, "annotation_txt")

    # empty dirs of dataset_transforms images/labels
    dest_pos = os.path.join(destination_dir, "positive")
    dest_neg = os.path.join(destination_dir, "negative")
    shutil.rmtree(dest_pos, ignore_errors=True)
    shutil.rmtree(dest_neg, ignore_errors=True)

    # destination paths
    dest_pos_images = os.path.join(dest_pos, "images")
    dest_pos_labels = os.path.join(dest_pos, "labels")

    # create dirs if necessary
    Path(dest_pos).mkdir(parents=True, exist_ok=True)
    Path(dest_neg).mkdir(parents=True, exist_ok=True)
    Path(dest_pos_images).mkdir(parents=True, exist_ok=True)
    Path(dest_pos_labels).mkdir(parents=True, exist_ok=True)

    # get List of case-paths
    # cases_positive = [f.name for f in os.scandir(dir_positive) if f.is_dir()]
    cases_negative = [f.path for f in os.scandir(dir_negative) if f.is_dir()]
    cases_labels = [f.path for f in os.scandir(dir_label) if f.is_file()]



    '''positive cases'''
    # for each positive case
    for filename in cases_labels:

        # Get all lines in a list, without ending \n
        # gets List of each frame for the case
        with open(filename) as f:    content = [i.strip() for i in f.readlines()]

        case_name = filename.split('\\')[-1].split('.')[0]
        img_dir = os.path.join(dir_positive, case_name)

        # create case-dirs if necessary
        dest_case_img = os.path.join(dest_pos_images, case_name)
        dest_case_lbl = os.path.join(dest_pos_labels, case_name)
        Path(dest_case_img).mkdir(parents=True, exist_ok=True)
        Path(dest_case_lbl).mkdir(parents=True, exist_ok=True)
        print(dest_case_img)



        # for each frame of a case
        for frame in content:
            ### Extract Info from Line
            image_file_name = frame.split()[0]
            bbox_info = frame.split()[1].split(',')
            bbox_coord = bbox_info[0:4]
            bbox_class = bbox_info[4]
            # print(image_file_name)
            # print(bbox_info)
            # print(bbox_coord)
            # print(bbox_class)


            ### Open Image
            img_path = os.path.join(img_dir, image_file_name)
            img = Image.open(img_path)
            img_size = exif_size(img)



            ### Transform coordinates of BBox
            min_Xcoordinate = int(bbox_info[0])
            min_Ycoordinate = int(bbox_info[1])
            max_Xcorrdinate = int(bbox_info[2])
            max_Ycoordinate = int(bbox_info[3])

            # get Center, Width & Height of BBox
            width = max_Xcorrdinate - min_Xcoordinate
            height = max_Ycoordinate - min_Ycoordinate
            center_X = int(min_Xcoordinate + (width/2))
            center_Y = int(min_Ycoordinate + (height / 2))

            # transform coords to normalized coords
                # divide x_center and width by image width, and y_center and height by image height
            norm_width = width / img_size[0]
            norm_height = height / img_size[1]
            norm_center_X = center_X / img_size[0]
            norm_center_Y = center_Y / img_size[1]


            ### Save in new directories

            # copy & resize images, keeping aspect ratio
            factor = img_size[0] / 640
            small_img = img.resize((640, int(img_size[1] // factor)), reducing_gap=3)

            small_img.save(os.path.join(dest_case_img, image_file_name))


            # create label files
            text_file_name = image_file_name.replace(".jpg", ".txt")
            text_file_path = (os.path.join(dest_case_lbl, text_file_name))


            with open(text_file_path, "w") as file:
                # class x_center y_center width height
                file.write(str(bbox_class)+" "+str(norm_center_X)+" "+str(norm_center_Y)+" "+str(norm_width)+" "+str(norm_height))




    '''negative cases'''
    # for each negative case
    for case in cases_negative:

        # create case-dirs if necessary
        case_name = case.split('\\')[-1].split('.')[0]
        dest_case_img = os.path.join(dest_neg, case_name)
        Path(dest_case_img).mkdir(parents=True, exist_ok=True)
        print(dest_case_img)

        # get frame paths for this case
        frames = [f.path for f in os.scandir(case) if f.is_file()]


        ### Open Image
        for frame in frames:

            img = Image.open(frame)
            img_size = exif_size(img)

            # copy & resize images
            factor = img_size[0] / 640
            small_img = img.resize((640, int(img_size[1] // factor)), reducing_gap=3)

            image_file_name = os.path.basename(frame)

            small_img.save(os.path.join(dest_case_img, image_file_name))






''' Create a random Training/Validation-Split, actually copies the images'''
"""
assumes:
    - NEEDS: dest_images_* need "images" in their paths
    - dir_data = result of resize_images_and_transform_labels()
        - holds:
            - "negative"-subdir has case-subdirs with neg. images
            - "positive"-subdir has subfolder images & labels, which have the case-subdirs;
            - labels are each frame one file (yolo-format)
    - validation_split      = % of the USED images, that will be validation
    - perc_of_all_neg_used  = % of neg. IMAGES that are going to be used, will take this perc. of each neg. case
    - perc_of_all_pos_used  = % of pos. IMAGES that are going to be used, will take this perc. of each pos. case
does:
    - DELETES existing dest_images_train & dest_images_val dirs with all contents
    - copies the actual images to create a tain/val-splitted dataset
    - replaces last "images" in dest_images_*-path with labels to use as dir to save labels
        - yoloV5 will understand this, it is the default behaviour for custom data
"""
def split_training_validation(dir_data="D:\\Master_Daten\\sundatabase_resized_normalized\\",
                              dest_images_train="D:\\Master_Daten\\sundatabase_yolo_split\\images\\train",
                              dest_images_val="D:\\Master_Daten\\sundatabase_yolo_split\\images\\val",
                              validation_split=0.2,
                              perc_of_all_neg_used=1.0,
                              perc_of_all_pos_used=1.0,
                              ):
    # get paths
    dir_positive = os.path.join(dir_data, "positive")
    dir_negative = os.path.join(dir_data, "negative")


    dir_positive_images = os.path.join(dir_positive, "images")
    dir_positive_labels = os.path.join(dir_positive, "labels")
    dest_labels_train = rreplace(dest_images_train, "images", "labels")
    dest_labels_val = rreplace(dest_images_val, "images", "labels")


    # empty dirs of dataset_transforms images/labels
    shutil.rmtree(dest_images_train, ignore_errors=True)
    shutil.rmtree(dest_images_val, ignore_errors=True)
    shutil.rmtree(dest_labels_train, ignore_errors=True)
    shutil.rmtree(dest_labels_val, ignore_errors=True)

    # create dirs if necessary
    Path(dest_images_train).mkdir(parents=True, exist_ok=True)
    Path(dest_images_val).mkdir(parents=True, exist_ok=True)
    Path(dest_labels_train).mkdir(parents=True, exist_ok=True)
    Path(dest_labels_val).mkdir(parents=True, exist_ok=True)



    #cases_positive = [f.path for f in os.scandir(dir_positive) if f.is_dir()]
    cases_positive = [f.path for f in os.scandir(dir_positive_images) if f.is_dir()]
    cases_negative = [f.path for f in os.scandir(dir_negative) if f.is_dir()]


    # create training/validation split for positive cases
        # casewise for positive, for negative not important if case or framewise
    val_size = int(len(cases_positive)*validation_split)
    val_cases = np.random.choice(cases_positive, size=val_size, replace=False)



    '''positive cases'''
    for case in cases_positive:

        # is part of the validation split?
        is_val = False
        if case in val_cases:
            is_val = True

        print(case)

        # get list of frames in this case
        frames = [f.path for f in os.scandir(case) if f.is_file()]

        # use only part of all available data?
        if not (0 < perc_of_all_pos_used <= 1):
            perc_of_all_pos_used = 1

        used_size = int(len(frames) * perc_of_all_pos_used)
        used_frames = np.random.choice(frames, size=used_size, replace=False)




        # for each used frame of a case
        for frame in used_frames:
            file_name = os.path.basename(frame)


            ### Save in new directories
            if is_val:
                dest_frame = os.path.join(dest_images_val, file_name)
            else:
                dest_frame = os.path.join(dest_images_train, file_name)

            shutil.copy(frame, dest_frame)


            ### copy label files
            label_path = rreplace(frame, "images", "labels").replace(".jpg", ".txt")
            file_name = file_name.replace(".jpg", ".txt")

            if is_val:
                dest_label = os.path.join(dest_labels_val, file_name)
            else:
                dest_label = os.path.join(dest_labels_train, file_name)

            shutil.copy(label_path, dest_label)





    '''negative cases'''
    for case in cases_negative:

        print(case)

        # get frame paths for this case
        frames = [f.path for f in os.scandir(case) if f.is_file()]

        # use only part of all available data?
        if not (0 < perc_of_all_neg_used <= 1):
            perc_of_all_neg_used = 1

        used_size = int(len(frames) * perc_of_all_neg_used)
        used_frames = np.random.choice(frames, size=used_size, replace=False)


        # create validation split
        val_size = int(len(used_frames) * validation_split)
        val_frames = np.random.choice(used_frames, size=val_size, replace=False)


        # for each used frame of a case
        for frame in used_frames:
            # is part of the validation split?
            is_val = False
            if frame in val_frames:
                is_val = True

            file_name = os.path.basename(frame)

            ### Save in new directories
            if is_val:
                dest_frame = os.path.join(dest_images_val, file_name)
            else:
                dest_frame = os.path.join(dest_images_train, file_name)

            shutil.copy(frame, dest_frame)





''' Create a random Training/Validation-Split, creates only a textfile with the image-paths, does not copy images'''
"""
assumes:
    - dir_data = result of resize_images_and_transform_labels()
        - holds:
            - "negative"-subdir has case-subdirs with neg. images
            - "positive"-subdir has subfolder images & labels, which have the case-subdirs;
            - labels are each frame one file (yolo-format)
    - dest_dir_text_files   = destination directory for the created text files
    - validation_split      = % of the USED images, that will be validation
    - perc_of_all_neg_used  = % of neg. IMAGES that are going to be used, will take this perc. of each neg. case
    - perc_of_all_pos_used  = % of pos. IMAGES that are going to be used, will take this perc. of each pos. case
does:
    - create two textfiles, one for training and one for validation, that contain the paths to the images
    - DELETES existing SUN_train.txt & SUN_val.txt in dest_dir_text_files
    - labels will automatically be found, since YOLOv5 locates labels automatically for each image by replacing the last instance of /images/ in each image path with /labels/
"""
def split_training_validation_textfile( dir_data = "D:\\Master_Daten\\sundatabase_resized_normalized\\",
                                        dest_dir_text_files="D:\\Master_Daten\\",
                                        validation_split=0.2,
                                        perc_of_all_neg_used=1.0,
                                        perc_of_all_pos_used=1.0,
                                        ):

    # get paths
    dir_positive = os.path.join(dir_data, "positive")
    dir_negative = os.path.join(dir_data, "negative")

    dir_positive_images = os.path.join(dir_positive, "images")
    dest_txt_train = os.path.join(dest_dir_text_files, "SUN_train.txt")
    dest_txt_val = os.path.join(dest_dir_text_files, "SUN_val.txt")


    # Create empty txt files, delete existing ones
    open(dest_txt_train, 'w').close()
    open(dest_txt_val, 'w').close()


    # get list of case-paths
    # cases_positive = [f.path for f in os.scandir(dir_positive) if f.is_dir()]
    cases_positive = [f.path for f in os.scandir(dir_positive_images) if f.is_dir()]
    cases_negative = [f.path for f in os.scandir(dir_negative) if f.is_dir()]


    # create training/validation split for positive cases
        # casewise for positive, for negative not important if case or framewise
    val_size = int(len(cases_positive) * validation_split)
    val_cases = np.random.choice(cases_positive, size=val_size, replace=False)

    '''positive cases'''
    for case in cases_positive:

        # is part of the validation split?
        is_val = False
        if case in val_cases:
            is_val = True

        print(case)

        frames = [f.path for f in os.scandir(case) if f.is_file()]

        # use only part of all available data?
        if not (0 < perc_of_all_pos_used <= 1):
            perc_of_all_pos_used = 1

        used_size = int(len(frames) * perc_of_all_pos_used)
        used_frames = np.random.choice(frames, size=used_size, replace=False)


        # for each frame of a case
        for frame in used_frames:

            ### Write to txt File
            if is_val:
                dest_txt = dest_txt_val
            else:
                dest_txt = dest_txt_train

            with open(dest_txt, "a") as file:
                # write Path to image
                file.write(frame + "\n")





    '''negative cases'''
    # use all available ones, just resize & copy
    for case in cases_negative:

        print(case)

        # get frame paths for this case
        frames = [f.path for f in os.scandir(case) if f.is_file()]

        # use only part of all available data?
        if not (0 < perc_of_all_neg_used <= 1):
            perc_of_all_neg_used = 1

        used_size = int(len(frames) * perc_of_all_neg_used)
        used_frames = np.random.choice(frames, size=used_size, replace=False)

        # create validation split
        val_size = int(len(used_frames) * validation_split)
        val_frames = np.random.choice(used_frames, size=val_size, replace=False)

        # for each used frame of a case
        for frame in used_frames:
            # is part of the validation split?
            is_val = False
            if frame in val_frames:
                is_val = True


            ### write to text-file
            if is_val:
                dest_txt = dest_txt_val
            else:
                dest_txt = dest_txt_train

            with open(dest_txt, "a") as file:
                # write Path to image
                file.write(frame + "\n")







if __name__ == '__main__':


    ### first transform original dataset into yolo-format
    # resize_images_and_transform_labels()



    ### then split into validation/training
    split_training_validation(dest_images_train="D:\\Master_Daten\\SUN_mini_2_pro\\images\\train",
                              dest_images_val="D:\\Master_Daten\\SUN_mini_2_pro\\images\\val",
                              validation_split=0.2,
                              perc_of_all_neg_used=0.02,
                              perc_of_all_pos_used=0.02,)
    #split_training_validation_textfile()




    exit(0)






