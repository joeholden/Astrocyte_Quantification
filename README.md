# Astrocyte_Quantification
This project takes in GFAP images of wholemount retinas and returns a heatmap version of the original image highlighting areas based on GFAP density. It also returns a histogram of density values (for tiles the image was split into and processed before re-stitching). Although designed for GFAP labeling analysis, there is no reason why it cannot be used for other IHC labeling as well. 

The program is not fully autonomous- it will require minimal hand processing of the image using ImageJ before running the python code. 

[ImageJ Processing]
1. Load your image into ImageJ. Subtract background using the rolling ball function. I find that rolling ball radius of 50px works well in most cases I have worked with. Adjust the brightness so it is easier to see- at this point it may look quite dim. Adjust brightness- and clicking auto twice seems to work well most of the time. Threshold your image appropriately. For GFAP images, I threshold so that fine processes are ~99-100% represented while avoiding background. 
2. The only other manual processing occurs as the user segments the wholemount retina from the background. In ImageJ simply use the polygon segment tool to create an ROI around the retina. Click 't' to add to the manager. Inverse the selection and delete to remove any staining outside of the tissue such as in the case of bubbles. Also if some samples have the optic nerve head in tact and others have a hole, for consistency, remove this region with a small circular ROI. Save this image as binary.png
3. You will also need a binary mask. Delete all the contents of a duplicated image in ImageJ- make sure it is binary. Show the ROI you made of the retina on the screen and hit 'ctrl F' to fill the ROI with white. Save this as mask.png. 
4. Place both binary.png in /binaries and mask.png in /masks (where root houses the batch.py program). You can add as many as you want... just name appropriately. If you want to look at colocalization from different channels, name the files consistently (channel_a binary.png , channel_a mask.png). Look at the code to see how data is zipped together in association. 

[Python] 
6. Move to a Python IDE (such as PyCharm) and run the rest of the code


Note:
batch.py is the script used in Holden et. al, 2022.
improved_heatmap.py improves upon the ideas of the original script but averages pixel intensities in an arbitrary window around each pixel. Additionally, it employs multiprocessing which greatly speeds up the runtime of the script, especially on large images. histogram_heatmap.py generates a histogram of these intensity values and is meant to be used with the improved_heatmap.py script. 

For the improved_heatmap.py and resize.py Good parameters are to scale down a 20x montaged retina by a factor of 13 and take density averages for a 20x20 px grid surrounding each pixel. 
