import os

# renames images to the format of case12-4

folder_holding_annotation_files = "D:\\Master_Daten\\sundatabase_positive\\annotation_txt"
images_path = "D:\\Master_Daten\\sunddatabase_stft\\Data\\"



os.chdir(folder_holding_annotation_files)


for case_file in os.listdir(folder_holding_annotation_files):
    if case_file.endswith("txt"):

        print(case_file)

        the_file = open(case_file, 'r')
        all_lines = the_file.readlines()
        case_name = os.path.basename(case_file).split('.')[0]
        case_number = int(case_name.split("case")[1])

        case_path = os.path.join(images_path, case_name)


        for row_index, row in enumerate(all_lines):
            image_name = row.split()[0]
            image_format = image_name.split(".")[-1]
            image_path = os.path.join(case_path, image_name)
            new_image_name = case_name+"-"+str(row_index+1)+"."+image_format
            new_image_path = os.path.join(case_path, new_image_name)

            os.rename(image_path, new_image_path)



#
#
# cases = [x[0] for x in os.walk(image_path)]
#
# cases.remove(image_path)
#
# for case in cases:
#     os.chdir(case)
#     filenames = next(os.walk(case), (None, None, []))[2]
#
#     print()
#     for idx, file in enumerate(filenames):
#         new_name = os.path.basename(case) + "-" + str(idx+1) + ".xml"
#         os.rename(file, new_name)
#
#
#
#
