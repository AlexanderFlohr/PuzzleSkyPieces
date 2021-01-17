# PuzzleSkyPieces


Puzzles with large areas of sky can be demanding. This small script is intended to assist you by
 separating single pieces according to their blue-color gradient. Details are shown below.
 
### Requirements:
* [Pillow-8.1.0](https://pypi.org/project/Pillow/) Required for image processing
### Input:
A .jpg file (or any other file type supported by Pillow) that contains a scan of blue puzzle pieces.
![](Images/example_scan.jpg){width=100 height=250}
Note: to obtain good results, one should leave a small space between the single parts.



 This small script allows you to reduce the number of pieces
by utilizing small color gradients. To be precise, the script tries to identify 4 different
