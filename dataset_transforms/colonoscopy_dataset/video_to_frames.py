# Importing all necessary libraries
import cv2
import os
import glob



def video_to_frame( data_path):
    """
    converts the found mp4 videos into a folder of the same name containing the numbered frames
    removes the video file
    :return:
    """

    video_files = [f for f in glob.glob(data_path + "/**/*.mp4", recursive=True)]


    for video in video_files:
        print(video)
        # Read the video from specified path
        cam = cv2.VideoCapture(video)

        try:

            # creating a folder named data
            dir_path = os.path.splitext(video)[0]
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        # if not created then raise error
        except OSError:
            print('Error: Creating directory of data')

        # frame
        currentframe = 0

        while (True):

            # reading from frame
            ret, frame = cam.read()

            if ret:
                # if video is still left continue creating images
                name = os.path.join(dir_path, str(currentframe) + '.png')

                # writing the extracted images
                cv2.imwrite(name, frame)

                # increasing counter so that it will
                # show how many frames are created
                currentframe += 1
            else:
                break

        # Release all space and windows once done
        cam.release()
        cv2.destroyAllWindows()
        os.remove(video)






if __name__ == '__main__':
    os.chdir("D:\Master_Daten")

    video_to_frame("colonoscopy_dataset/")

    exit(0)
