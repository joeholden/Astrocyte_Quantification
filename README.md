# Astrocyte_Quantification
This project takes in GFAP images of wholemount retinas and returns a heatmap version of the original image highlighting areas based on GFAP density. It also returns a histogram of density values (for tiles the image was split into and processed before re-stitching).

The program is not fully autonomous yet- it will require minimal hand processing of the image and using both ImageJ and Python. 

1. To begin, download the imageJ macro. This does pre-processing of the image (rolling-ball processing with 50 px radius, adjusting brightness, thresholding the image to remove background, and makes the image binary. It will also save the file to a directory of your choosing.
2. The only manual processing occurs as the user segments the wholemount retina from the background. In ImageJ simply use the polygon segment tool to create an ROI around the retina. Click 't' to add to the manager. Inverse the selection and delete to remove any staining outside of the tissue like for bubbles. Invert the ROI back and flatten it. Save this image as a .tif
3. Move to Python and run the rest of the code
