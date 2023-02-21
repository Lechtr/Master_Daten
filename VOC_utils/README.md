The utility files in this folder assume that the files are in the following file structure.
They are used to process the datasets after they have been converted to the VOC-Format

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
