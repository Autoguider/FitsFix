from astropy.io import fits
from argparse import ArgumentParser
import glob
import numpy as np
import csv
import os


def format2string(pref, width, mylist):
    sss = pref
    frame = width
    for z in mylist:
        k = frame - len(str(z))
        for i in range(1, k):
            sss = sss + " "
        sss = sss + str(z) + "|"
    return sss


def csv_exists():
    file_list_csv = glob.glob("defects.csv")
    if len(file_list_csv) != 0:
        scan_new = input('file "defects.csv" found - use ? y/N ')
        if scan_new == "N":
            try:
                os.remove('defects.csv')
            except IOError as ef:
                print("I/O error({0}): {1}".format(ef.errno, ef.strerror))
                print('cannot delete "defects.csv" file')
                input('press key to exit ')
                exit()

            return False  # now it does not exist anymore
        else:
            print('existing "defects.csv" will be used\n')
            return True  # file to be used - no scanning required
    else:
        return False  # no file found


def ini_file_exist():
    ini_list = glob.glob("Fix.ini")
    if len(ini_list) != 0:
        print("Found Fix.ini - using existing Fix.ini")
        return True
    else:
        return False


def create_directory4_fixed():
    if not os.path.exists('Fixed'):
        os.makedirs("Fixed")  # create
    else:
        # print('Directory exists Overwrite ? Y/n')
        files_in_directory = os.listdir("Fixed")
        if len(files_in_directory) > 0:
            reply = input('Directory "Fixed" contains files, Erase ? Y/n')
            if reply == 'Y':
                try:
                    for z in files_in_directory:
                        os.remove('Fixed/' + z)
                except IOError as ef:
                    print("I/O error({0}): {1}".format(ef.errno, ef.strerror))
                    print('Cannot delete file in directory "Fixed"')
                    input('press key to exit ')
                    exit()

            else:
                input('Press any key - program aborted')
                exit()


def repair_file(file2process):
    try:
        raw_fits = fits.open(file2process)
    except IOError as fe:
        print("I/O error({0}): {1}".format(file2process, 'Cannot open'))
        # print("I/O error({0}): {1}".format(fe.errno, fe.strerror))
        input('press key to exit ')
        exit()

    img_hdr = raw_fits[0].header  # get header to document where correction was done
    if (img_hdr['BITPIX'] != (-32) and img_hdr['BITPIX'] != -64):  # if floating point
        img_data = raw_fits[0].data  # image data
        source = img_data

        if Bayer is True:
            compare_right = np.roll(source, -2, axis=1)  # shift 2cols left
            compare_left = np.roll(source, 2, axis=1)  # shift 2cols left
        else:
            compare_right = np.roll(source, -1, axis=1)  # shift 1col left
            compare_left = np.roll(source, 1, axis=1)  # shift 1col left
        average_array = compare_right + compare_left  # building averaged values for correction
        average_array = average_array // 2  # integer division sufficient accurate for later use
        for i in cols2repair:
            source[:, int(i)] = average_array[:, int(i)]  # exchange of the values
        entry = ""
        for i in cols2repair:  # ensure to deal with integers
            k = int(i)
            entry = entry + str(k) + '; '
        entry.rstrip()
        newentry = entry[:-2]
        if len(newentry) < 45:
            img_hdr.set('ColCorr', newentry, 'tweaked columns')
        else:
            newentry = newentry[:45] + '...'
        entry.rstrip(";")  # remove last semicolon
        img_hdr.set('ColCorr', newentry, 'tweaked columns')
        cwd = os.getcwd()
        accessed = (os.path.getatime(file2process))
        modified = (os.path.getmtime(file2process))
        s = cwd + '/Fixed/' + file2process
        sep = '.'
        erg = s.rpartition(sep)
        save_as_name = erg[0] + 'C' + erg[1] + erg[2]
        try:
            raw_fits.writeto(save_as_name)
            print(save_as_name + ' repaired')
        except IOError as err:
            print("I/O error({0}): {1}".format(err.errno, err.strerror))
            input('press key to exit ')
            exit()

        tup = (accessed, modified)  # modify timestamp
        os.utime(save_as_name, tup)
        global no_filesrepaired
        no_filesrepaired += 1
    else:
        print(file2process + ' is floating point -> no repair')
        global no_filesrejected
        no_filesrejected += 1
    raw_fits.close()


def scanfits(file2process):
    try:
        scan_raw = fits.open(file2process)
    except IOError as err:
        print("At scanning I/O error({0}): {1}".format(err.errno, err.strerror))
        input('press key to exit ')
        exit()
    # hdr = hdul[0].header  # get header to document where correction was done
    scan_data = scan_raw[0].data  # image data
    scan_header = scan_raw[0].header
    result = scan_header['BITPIX']

    if (scan_header['BITPIX'] != (-32) and scan_header['BITPIX'] != -64):  # if floating point
        #print('Image ' + file2process +' is on floating point data - please remove from directory\n')
        #input('Abort program - Press key ')
        #exit()
        source = scan_data  # ndarray from fits-file; Just a reference - no deep copy
        source_offset = source + args.Threshold_Intensity  # add permitted tolerance

        if Bayer is True:
            compare_right = np.roll(source, -2, axis=1)  # shift 2cols left
            compare_left = np.roll(source, 2, axis=1)  # shift 2cols left

        else:
            compare_right = np.roll(source, -1, axis=1)  # shift 1col left
            compare_left = np.roll(source, 1, axis=1)  # shift 1col left
        comresright = source_offset < compare_right  # reduce to boolean values
        comresleft = source_offset < compare_left
        comresleft = comresleft & comresright  # True only if in both compare array
        global count
        count = np.count_nonzero(comresleft, axis=0)  # number of "TRUEs" per column
        count[count <= AllowedDefectPerCol] = 0  # set to 0 if less TRUEs than allowed
        count[count > 0] = 1  # set to 1 for adding to an accumulator
        global Accumulator  # required because global variable is changed from inside this function
        Accumulator = Accumulator + count
        print((file2process + '  scanned'))
    else:
        print((file2process + ' floating point-> skipped '))
    scan_raw.close()



##############################################################################################
#  Start of program
##############################################################################################

#     Evaluate Commandline Args

parser = ArgumentParser()
parser.add_argument("-t", "--type", dest="Image_Kind", default="r", choices=["r", "m"],
                    help="r (= default) for RGB color, m for monochrome")
parser.add_argument("-m", "--mode", dest="Operation_Mode", default="sr", choices=["sr", "s", "r"],
                    help="sr scan & repair(= default), s scan only, r repair only,needs defects.csv in working direct.")
parser.add_argument("-p", "--perc", dest="PercentsInCol", type=int, default=25,
                    help="tolerated percentage of defects per columns default =20  input range 10..80 ")
parser.add_argument("-thr", "--thres", dest="Threshold_Intensity", type=int, default=50,
                    help="tolerated difference in ADUs to neighbor col. elements default = 50 input range 30..3000")

# Accumulator = np.zeros(0)   #Define it as global
Bayer = True  # True = Bayer Matrix = default value
# FirstImage = True
args = parser.parse_args()
Image_type = args.Image_Kind
Operation_type = args.Operation_Mode
percentage_value = args.PercentsInCol
threshold_value = args.Threshold_Intensity

# parameters from Fix.ini override command line args

getfrom_ini = ini_file_exist()
if getfrom_ini == True:
    with open('Fix.ini', 'r') as read_obj:
        csv_reader = csv.reader(read_obj, delimiter=';')
        arguments = list(csv_reader)  # list of lists
    read_obj.close()
    extr_args = arguments[0]
    Image_type = extr_args[0]
    Operation_type = extr_args[1]
    percentage_value = int( extr_args[2])
    threshold_value = int(extr_args[3])





if Image_type == "m":
    Bayer = False
# -------------------------

Program_Mode = "scan&repair"  # to be safe -set the default value
if Operation_type == "sr":
    Program_Mode = "scan&repair"
if Operation_type == "s":
    Program_Mode = "scan"
if Operation_type == "r":
    Program_Mode = "repair"

if percentage_value < 10 or percentage_value > 80:
    print('percentage out of range 10...80')
    print('please restart with value 10...80')
    input('exit program press any key')
    exit()

if threshold_value < 30 or threshold_value > 3000:
    print('value out of allowed range 30...3000')
    print('please restart with value in range 30...3000')
    input('exit program press any key ')
    exit()

print('FixTheFits has Started\n')

Datafiles = glob.glob('*.fit*')
if len(Datafiles) == 0:
    input('No fits found - program abort Press key')
    exit()
else:
    try:
        hdul = fits.open(Datafiles[0])
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        input('press key to exit ')
        exit()

hdr = hdul[0].header  # get data from header to get parameters for scan and repair
data = hdul[0].data  # image data
Accumulator = np.zeros(data.shape[1], dtype=np.int32)  # count how often error in column was detected
count = np.zeros(data.shape[1], dtype=np.int32)
max_cols = data.shape[1]
if hdr['NAXIS'] > 2:  # if color converted
    input('Image seems to be color converted - Abort program - Press key ')
    exit()


AllowedDefectPerCol = data.shape[0] * args.PercentsInCol // 100

try:
    camera_name = hdr['INSTRUME']

except KeyError:
    camera_name = ''
hdul.close()

csv_valid = csv_exists()  # check for file defects.csv in current working directory

# For repair only a formerly created/ copied defects.csv is required
if (csv_valid is False) and (Program_Mode == "repair"):
    input('no defects.csv found - repair not possible - abort program Press any key')
    exit()

if ((Program_Mode == "scan") or (Program_Mode == "scan&repair")) and (csv_valid is False):
    print('Scannning fits files')
    for file2check in Datafiles:
        scanfits(file2check)

    counted = (Accumulator[np.where(Accumulator > 0)])
    indexes = np.where(Accumulator > 0)[0]
    # remove 1st 2 entries in case of Bayer matrix else it is monochrome

    if indexes[0] == 0:
        newIndexes = np.delete(indexes, [0])
        newCounted = np.delete(counted, [0])
    if newIndexes[-1] == max_cols -1 :
        newIndexes = np.delete(newIndexes, [-1])
        newCounted = np.delete(newCounted, [-1])



    print('\nResults of scan :')
    print(format2string("times counted :", 7, newCounted))

    print(format2string("in column     :", 7, newIndexes))
    occurrlimit = int(len(Datafiles) * 0.3)
    i = np.where(newCounted >= occurrlimit)
    output = newIndexes[i]

    with open('defects.csv', 'w', newline='') as csvfile:
        resultwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        resultwriter.writerow(output)
        s = ''.join(str(x) for x in output)
        h = len(s) + len(output) - 1
        resultwriter.writerow('')
        if len(camera_name) > 0:
            dummy = ['Camera:', camera_name]
            resultwriter.writerow(dummy)

    csvfile.close()
    print('\nNew file "defects.csv" written to current directory')
    print('mapped ' + str(output) + ' as defect columns in file\n')
    if Program_Mode == "scan":
        input("Scanning done - results in defects.csv -press any key to quit")
        exit()
# ###################################################################
# Begin of repair mode
# ###################################################################


with open('defects.csv', 'r') as read_obj:
    csv_reader = csv.reader(read_obj, delimiter=';')
    cols2repair = list(csv_reader)  # list of lists
read_obj.close()
cols2repair = cols2repair[0]
if len(cols2repair) == 0:
    input('No columns to correct indicated in file - Abort program Press key')
    exit()
for nn in cols2repair:
    k = nn.isnumeric()
    if k is False:
        input('Non numeric value in "defects.csv" - Abort program Press key')
        exit()

for nn in cols2repair:
    k = int(nn)
    if k > max_cols:
        input('Value ' + nn + ' in "defects.csv" exceeds ' + str(max_cols) + ' - Abort program Press key')
        exit()

create_directory4_fixed()
no_filesrepaired = 0
no_filesrejected = 0
for file2repair in Datafiles:
    repair_file(file2repair)

print('\n*** files repaired: ' + str(no_filesrepaired) + ' ***')
if no_filesrejected > 0:
    print('*** files rejected: ' + str(no_filesrejected) + ' ***')
input('\nTo exit program - press key')
