import glob
import os
import shutil
from pathlib import Path



def create_stft_dataloader_txt_files( data_path ):
    """
    create stft_dataloader files in for a whole dataset
    expects as param a dir of a dataset with the subdirs "Annotation" and "Image"

    :param data_path:
    :return: creates text file with one line per frames of the dataset for all frames with the format: dir frame_id frame_id max_frame
    so example case4 2 2 259
    """

    # iter through all subdirs
    with open(os.path.join(data_path, 'stft_dataloader_KUMC.txt'), 'w', encoding='utf-8') as f:
        for vid_dir in Path(os.path.join(data_path, "Image")).iterdir():
            if vid_dir.is_dir():
                print()
                print(vid_dir)
                i = 1

                # find max frame of vid
                max_frame = str(max([int(f.stem) for f in vid_dir.glob("*.jpg")]))

                # sort after numerical order, not important but nicer
                images = sorted([f for f in vid_dir.glob("*.jpg")], key=lambda file: int(file.stem))
                for img in images:
                    f.write(vid_dir.stem + " " + img.stem + " " + img.stem + " " + max_frame + "\n")







if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    create_stft_dataloader_txt_files("processed_data/KUMC/")
    exit(0)
