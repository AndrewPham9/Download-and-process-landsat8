# Download-and-process-landsat8

Tool automate process-landsat8
prepare to have 2 python 2 and 3 machine. recommend 2.7 and 3.6
install all <weird_lib_of_this_project>
______________________________________________________________________________________________
1) put db.txt and py_machine.txt in the folder you want to write final result and run program
in db.txt is information of  database manager system
in py_machine is path to your py2 and py3 scripts where contain gdal_<something>.py
i have already put examples of my database and py scipts there, so you should change to your.

2) open cmd
cd to  <your run folder>
examples:
D:  >>enter
D:\Download-and-process-landsat8 >>enter

3) run
py -3 <folder_contain_all_these_code>/dtek2.py -s <your_wanted_shp_at_long_lat_coord> -d <yourdate> -p <your_Location_Name>
location_Name should be the same for many date of your location.

example:
py -3 D:\python\STAC_intern_project\Download-and-process-landsat8\dtek2.py -s D:\python\STAC_intern_project\Download-and-process-landsat8\HCM\HCM.shp -d 20150209 -p HoChiMinh

_____________________________thank you for choosing my scipts!_____________________________