# Library for the mink eradication

###############################################################
# FUNCTIONS
#
#
#   handle_log: Sends a text string to a function which writes to
#               a file and/or stdout
#
#   dissolve:   Per reference to an article on how the ESRI
#               dissolve functionality can be made better using
#               the ESRI dissolve functionality.
#
#
#
#

###############################################################
# Function to handle contionous info to user(stdout) and log
#

def handle_log(contentstring,destination, path_maps_result):

    file_log_name        = "log.txt"

    if (destination=="stdout,file"):

        print(contentstring)


        loggfile = "%s%s" % (path_maps_result,file_log_name)

        current_file    = open(loggfile, 'a')

        current_file.write(contentstring)

        current_file.closed


    elif (destination=="stdout"):

        print(contentstring)


    elif (destination=="file"):

        loggfile = "%s%s" % (path_maps_result,file_log_name)

        current_file    = open(loggfile, 'a')

        current_file.write(contentstring)

        current_file.closed


    else:
        print ""




###############################################################
# Divide and conquer dissolve
#
# Specialized sub-dissolve based on group size. Bacause ESRI
# didn't get it right.
#
# Read more about the needs for this function on this page:
#
#    http://www.mindland.com/wp/solving-the-arcpy-dissolve/
#
def dec_dissolve(file_in, file_out, group_by):

    count           =  0
    current_min     =  0
    current_max     =  group_by
    joinstring      =  []


    features_total    =  int(arcpy.GetCount_management(file_in).getOutput(0))


    while (current_max < (features_total+group_by)):

        resulting_file  = "%sbuffer_result_%s.shp" % (path_maps_basis,count)

        where_clause    = '"FID"> %s AND "FID" <= %s' %(current_min,current_max)

        arcpy.Select_analysis(file_in, resulting_file, where_clause)


        resulting_file_d = "%sbuffer_result_d_%s.shp" % (path_maps_basis,count)

        arcpy.Dissolve_management(resulting_file, resulting_file_d,"","","SINGLE_PART","")

        # delete temporary files
        arcpy.Delete_management(resulting_file)


        joinstring.append(resulting_file_d)

        current_min = group_by*count
        current_max = current_min + group_by

        count +=1


    resultbuffer = "%sresultbuffer.shp" % (path_maps_basis)

    arcpy.Merge_management(joinstring, resultbuffer,"")

    # delete temporary files
    for shapefile in joinstring:

        arcpy.Delete_management(shapefile)


    arcpy.Dissolve_management(resultbuffer, file_out,"","","SINGLE_PART","")


    # delete temporary files
    arcpy.Delete_management(resultbuffer)



    # Clean up destination folders
    # for files in os.walk(path_maps_process, topdown=False):
    #    for name in files:
    #        print name
    #        os.remove(os.path.join(path_maps_process, name))
