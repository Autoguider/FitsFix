# FitsFix
### command-line utility to find and repair defect columns in (CCD) astronomical images in fits-format

> Due to the facts that I have a camera with a few "strange" columns Sander Pool's utility Fixfits seems not to be available anymore, I wrote a python script that helps to fix defect columns in images. As I do not dither the darker "strange" columns add up or spread over appr. 10 columns after stacking, looking nasty. 
> 
> The script is designed to find and replace **single** defect columns in amateur astronomical CCD images in fits format. It does not find defects in case **logically** (e.g. for Bayer matrix) neighboring columns do have the same problem in brightness. In case columns that are too bright needs to be corrected, then add the column nunber to the defect.csv file. 
It is not tested for CMOS cameras becasue it is not clear to me if column related issues occur also with CMOS cameras. Not tested yet.
> 
> Default is for CCDs with Bayer Matrix. (Not tested for monochromes yet)
> Fixing has to take place **before** converting to color.
> Image data is in (16 bit) **integer** format.
> The idea for usage is to copy FitsFix.py (and the Fix.ini file unless you go with the default parameters) to the directory that contains the fits files and run it. The fixed images are stored in the sub-directory Fixed. The names of the fixed files are easy to identify by the letter C added to the name of the original file. Access time is preserved for easy referencing the date/time of the exposure. The indexes of the columns modified by the program are documented in the fits-header at the key COLCORR limited to the length of line = 80 chars. If more colums are corrected then ... will show up in the fits header value.
By default only those columns are recorded in the defects.csv file that occur at least in 30 % of the images. Feel free to add further colums to the defects.csv. Watch for the semicolons.(See example).
> You may copy an applicable defects.csv file from a former scan in case you want to skip scanning for defect columns to the image directory and run FitsFix.
> Added feature with Fix.ini file. It has the same structure as the parameters of the command line. The fix.ini files parameters override the command line parameters. The parameters are separated by semi colons.
>
> The program checks if the colums are darker by comparing in measuring units of ***integer*** ADUs It cannot handle floating point values for the pixel intensity properly. Applying the repair to floating point files dilutes the result. Applying the fitsFix procedure to normalized master darks, e.g. created by SIRIL makes them unusable. So remove the floating-point containing file from the input list. 
