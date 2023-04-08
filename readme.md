# FitsFix
### command-line utility to find and repair defect columns in astronomical images in fits-format

> Due to the facts that I have a camera with a few "strange" columns Sander Pool's utility Fixfits seems not to be available anymore, I wrote a python script that helps to fix defect columns in images. As I do not dither the darker "strange" columns add up or spread over appr. 10 columns after stacking, looking nasty. 
> 
> The script is designed to find and replace **single** defect columns in amateur astronomical CCD images in fits format.
> 
> Default is for CCDs with Bayer Matrix. (Not tested for monochromes yet)
> Fixing has to take place **before** converting to color.
> Image data is in (16 bit) integer format.
> The idea for usage is to copy FitsFix.py to the directory that contains the fits files and run it. The fixed images are stored in the sub-directory Fixed. The names of the fixed files are easy to identify by the letter C added to the name of the original file. Access time is preserved for easy referencing the date/time of the exposure. The indexes of the columns modified by the program are documented in the fits-header at the key COLCORR
> You may copy an applicable defects.csv file from a former scan in case you want to skip scanning for defect columns to the image directory and run FitsFix.
