# ---------------------------------------------------------------------------
# mink_calculation_islands.py
#
# This script calculates potential areas for figting alien species
# in coastal areas. It looks at clustered islands and their (naerhet)
# Based on this natural clusters will be found. Their closeness to
# the shoreline is also visualized.
#
# Input:         * islands.shp
#                * protected_areas.shp
#
#
# Output:        * visual_zones.shp
#                * coastline_riskzone.shp
#
# Prerequisites: * The ESRI ArcPy library
#
# ---------------------------------------------------------------------------


# Import modules
import arcpy, os
from datetime import datetime,date,time
from time import gmtime, strftime, localtime

startTime = datetime.now()

###############################################################
# FUNCTIONS





###############################################################
# Function to handle contionous info to user(stdout) and log
#

def handle_log(contentstring,destination):

    if (destination=="stdout,file"):
        print contentstring
    elif (destination=="stdout"):
        print contentstring
    elif (destination=="file"):
        print contentstring
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
def dec_dissolve(file_in, file_out,group_by):

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





################################################################
# Define variables


path_project                  = "C:/arikiv_temp/minknomore/"

path_maps_basis               = "%smaps_basis/"   % (path_project)
path_maps_process             = "%smaps_process/" % (path_project)
path_maps_result              = "%smaps_result/"  % (path_project)

to_file                       = ""

log_file                      = "log.txt"
log_destination               = "stdout,file"

list_buffer_distance_m        = 2000
max_distancetoshore_possible  = 200000
i                             = 1

county_nr                     = 9

county_name                   = "aust-agder"
projectionfile                = "%swgs84_utm_33n.prj" % (path_maps_basis)
coastline                     = "%snorge_fastland_kystlinje.shp" % (path_maps_basis)
islands_all                   = "%sOyer_AustAgder_100m.shp" % (path_maps_basis)
run_time_start                = strftime("%d/%m/%Y  %H:%M:%S", localtime())

log_setting                   = "stdout,file"


path_maps_result            = "%s%s/" % (path_maps_result,county_nr)


################################################################
#

to_log               += "Calculation of zones suitable for decimation of american mink\n"
to_log               += "#############################################################\n\n\n"
to_log               += "Calculation started   : %s \n\n\n" % (run_time_start)
to_log               += "\n"
to_log               += "\n"
to_log               += " Basis for this calculation:\n"
to_log               += "\n"
to_log               += "\n"
to_log               += "\n"
to_log               += " Responsible              : Ragnvald Larsen (rla@dirnat.no)"
to_log               += "\n"
to_log               += "\n"
to_log               += " Buffer distance (meters) : %s \n" % (list_buffer_distance_m)
to_log               += "\n"
to_log               += " County                    : %s (nr: %s) \n" % (county_name, county_nr)
to_log               += "\n"
to_log               += " Projection               : %s\n" % (projectionfile)


handle_log(to_file,"stdout,file")



# Coastline file

to_file               += "\n"
to_file               += " Coastline: %s\n" % (coastline)

to_file               += "\n"
to_file               += " Islands file: %s\n" % (islands_all)

number_islands_tostartwith = int(str(arcpy.GetCount_management(islands_all)))
print " Islands in area      : %s" % (number_islands_tostartwith)
print"\n"

to_file               += "\n"
to_file               += " Numbeer of islands in this calculation: %s\n" % (number_islands_tostartwith)


islands_affected_total      = "%sf_%s_islands_affected_total.shp" % (path_maps_result,county_nr)

print "- Touch islands_affected_total_temp"

islands_affected_total_nopath = "f_%s_islands_affected_total.shp" % (county_nr)

arcpy.CreateFeatureclass_management(path_maps_result, islands_affected_total_nopath, "POLYGON")
arcpy.DefineProjection_management(islands_affected_total, projectionfile)

islands_affected_total_temp = "%sislands_affected_total_temp.shp" % (path_maps_process)


# clip the coastal area to a subset to ease the distance calculations later in the procedure




# A polygon shapefile with protected areas. One of the object
# attributes in this calculation is VERNEF_ID. We could use it
# to filter our protected areas (assets).
areas_protected = "%snaturvernomrader_utm33.shp" % (path_maps_basis)



# Copy all islands to process folder where a file will keep all
# files not affected by the evaluation. Through our calculation
# we will remove islands from this file until our iterations has
# run throughout
print "- Copying all islands to process folder"
islands_left        = "%sislands_left.shp" % (path_maps_process)

arcpy.Copy_management(islands_all, islands_left)

arcpy.DefineProjection_management(islands_left, projectionfile)



# Join the protected areas with the islands. Our target objects
# are the islands, so whatever joins we get with the protected
# areas will add up in the Join_Count variable
print "- Joining protected areas and islands"
islands_affected_joined = "%sislands_affected_joined.shp" % (path_maps_process)
arcpy.SpatialJoin_analysis(islands_left, areas_protected, islands_affected_joined)


# Select all islands which are overlapped with one or more protected areas.
# Deposit the joins in a new file (islands_affected).
#
print "- Creating a shapefile representing islands with protection status"
islands_affected     = "%sislands_affected.shp" % (path_maps_process)
where_clause         = '"Join_Count" > 0'
arcpy.Select_analysis(islands_affected_joined, islands_affected, where_clause)


# Clean up: Delete temporary joined file
print "- Deleting temporary join file"
arcpy.Delete_management(islands_affected_joined)


islands_left_new        = "%sislands_left_new.shp" % (path_maps_process)

# Delete affected islands from our store of non-affected islands
# The file will be used as a basis for later buffering.
#
print "- Erasing protected/affected islands from all islands"
arcpy.Erase_analysis(islands_left,islands_affected,islands_left_new)
arcpy.Delete_management(islands_left)
arcpy.Copy_management(islands_left_new, islands_left)
arcpy.Delete_management(islands_left_new)

arcpy.DefineProjection_management(islands_left, projectionfile)




#######################################################################
#
# The iteration process uses the affected islands as a basis for
# further calculations.
#
# In short affected islands (our assets) will be subsequently
# buffered and all new affected islands are stored in a new
# shapefile. The affected islands are erased from our shapefile
# consisting of islands left. This game continues until the
# iteration exchaustion; either by all islands being affected, or
# until the "spread" stops.
#

#Add unrealistically high number of islands as initial values
number_islands_left      = 199999
number_islands_left_last = 200000


#Fortsettes så lenge det kommer nye øyer inn i beregningen, eller beregningen når land.
print "- Entering loop for iterations"
while (number_islands_left < number_islands_left_last):

    print "-- Starting loop for analysis. Run #%s" % (i)


    starttimeround = datetime.now()


    # Setting up variables
    current_buffer_temp        = "%sbuffer_temp.shp"        % (path_maps_process)

    current_buffer_temp_temp   = "%sbuffer_temp_temp.shp"   % (path_maps_process)

    current_buffer             = "%sbuffer_%s.shp"          % (path_maps_process,i)

    ################################################
    # B U F F E R S
    #
    # Buffer around all islands
    #
    printstring                =  islands_affected[80:]
    print  "--- Buffering  : [..]%s" % printstring

    distanceField              = "%s Meters" % (list_buffer_distance_m)
    sideType                   = ""
    endType                    = ""
    dissolveType               = "NONE"
    dissolveField              = ""
    arcpy.Buffer_analysis(islands_affected, current_buffer_temp, distanceField, sideType, endType, dissolveType, dissolveField)

    arcpy.DefineProjection_management(current_buffer_temp, projectionfile)

    if i>1:

        # If this is not the first buffer the older buffer is merged with the new buffer
        # This way we will get a full coverage buffer under all hitherto affected islands

        print "--- Making a full size buffer and clean it up. This integrates buffer #%s" % (i)

        formeriterator   = i-1

        formerbuffer     = "%sbuffer_%s.shp"          % (path_maps_process,formeriterator)

        arcpy.Merge_management([formerbuffer,current_buffer_temp], current_buffer_temp_temp)
        arcpy.Delete_management(current_buffer_temp)

        arcpy.Copy_management(current_buffer_temp_temp, current_buffer_temp)
        arcpy.Delete_management(current_buffer_temp_temp)





    #Repair the geometries made by ESRI.
    arcpy.RepairGeometry_management(current_buffer_temp, "Keep_NULL")

    #Disssolve
    printstring          =  current_buffer_temp[80:]
    print  "--- Dissolving : [..]%s" % printstring

    print "Normal DISSOLVE"
    #dec_dissolve(current_buffer_temp, current_buffer,1000)

    arcpy.Dissolve_management(current_buffer_temp, current_buffer,"","","SINGLE_PART","")

    arcpy.DefineProjection_management(current_buffer, projectionfile)


    # Clean up
    print "--- Deleting temporary buffer file"
    arcpy.Delete_management(current_buffer_temp)


    # Add relative field for affected islands
    fieldname = "islev_%s" % (i)
    arcpy.AddField_management(current_buffer,fieldname,"LONG", 9, "", "","","NULLABLE")

    # Update is_lev_# value with 1
    rows = arcpy.UpdateCursor(current_buffer)
    for row in rows:
        row.setValue(fieldname,"1")
        rows.updateRow(row)



    print "--- Joining protected areas and islands"
    arcpy.SpatialJoin_analysis(islands_left, current_buffer, islands_affected_joined)



    ################################################################
    #Select all islands with more than one protected area status and make a new layer
    #
    print "--- Creating a shapefile representing islands with protection status"
    islands_affected        = "%sislands_affected_%s.shp" % (path_maps_process,i)
    where_clause ='"Join_Count" > 0'
    arcpy.Select_analysis(islands_affected_joined, islands_affected, where_clause)
    arcpy.DefineProjection_management(islands_affected, projectionfile)


    # Clean up: Delete temporary joined file
    print "--- Deleting temporary join file"
    arcpy.Delete_management(islands_affected_joined)

    # add identification field to the islands affected
    fieldname = "isl_lev"
    arcpy.AddField_management(islands_affected,fieldname,"LONG", 9, "", "","","NULLABLE")

    rows = arcpy.UpdateCursor(islands_affected)

    for row in rows:

        row.setValue("isl_lev",i)
        rows.updateRow(row)


    # Add the new islands to the original one
    print "--- Merging new islands into islands_affected_total"


    arcpy.Merge_management([islands_affected_total, islands_affected], islands_affected_total_temp)
    arcpy.Delete_management(islands_affected_total)
    arcpy.Copy_management(islands_affected_total_temp, islands_affected_total)
    arcpy.Delete_management(islands_affected_total_temp)


    # Delete affected islands from islands_left
    print "--- Erasing infected islands from all islands"
    arcpy.Erase_analysis(islands_left,islands_affected,islands_left_new)
    arcpy.Delete_management(islands_left)
    arcpy.Copy_management(islands_left_new, islands_left)
    arcpy.Delete_management(islands_left_new)

    timestamp = (datetime.now()-starttimeround)


    #remove all islands within a buffer of n meters away from the coastline


    number_islands_left_last = number_islands_left
    number_islands_left = int(str(arcpy.GetCount_management(islands_left)))

    print "--- Islands left: %s" % (number_islands_left)

    print "This round took: %s" % (timestamp)

    i+=1

print "--"
print "-- Iterations has ended"
# union for all buffers affected


# write to file
to_file += " Antall øyer som ikke inngår i minkbekjempelsessoner er: %s" % number_islands_left
to_file               += "\n"
to_file               += "\n"

#Start counting again
starttimeround = datetime.now()

count=1

unionlist=""

print "-- Merging (union) between all buffer objects"
while count < i:

    unionobject   = "%sbuffer_%s.shp" % (path_maps_process,count)

    if count>1:
        unionlist = unionlist + ";" + unionobject
    else:
        unionlist = unionobject


    count+=1


full_buffer_temp  = "%sfullbuffer_temp.shp"   % (path_maps_process)


arcpy.Union_analysis(unionlist,full_buffer_temp)


# Add a field in the buffer to keep summarized values
fieldname = "isl_lev"
arcpy.AddField_management(full_buffer_temp,fieldname,"LONG", 9, "", "","","NULLABLE")

count=1

# Update is_lev_# value with 1
rows = arcpy.UpdateCursor(full_buffer_temp)

print "-- Adding island level (isl_lev) to the buffer based on respective buffer level values."
for row in rows:
    count   =1
    sumpost = 0
    while count<i:

        possiblefieldname = "islev_%s" % (count)

        sumpost           = sumpost + row.getValue(possiblefieldname)

        count+=1

    vicinityfactor        = i-sumpost

    row.setValue("isl_lev",vicinityfactor)
    rows.updateRow(row)



# Join islands_affected and islands_affected_total


islands_infested     = "%sislands_in_zones.shp" % (path_maps_result)

islands_affected     = "%sislands_affected.shp" % (path_maps_process)

print "--- Merging affected islands and affected_total to islands_infested.shp"

arcpy.Merge_management([islands_affected,islands_affected_total], islands_infested)
arcpy.DefineProjection_management(islands_infested, projectionfile)


#buffer around all islands
visual_buffer_temp   = "%svisual_buffer_temp.shp" % (path_maps_process)


visual_buffer        = "%sf_%s_visual_buffer.shp" % (path_maps_result,county_nr)

printstring          =  visual_buffer[80:]
print "--- Making visual buffer  : [..]%s" % printstring


# the visual buffer should be half of the total potential swimming distance
distanceField        = "%s Meters" % (list_buffer_distance_m/2)
sideType             = ""
endType              = ""
dissolveType         = "NONE"
dissolveField        = ""
arcpy.Buffer_analysis(islands_infested, visual_buffer_temp, distanceField, sideType, endType, dissolveType, dissolveField)


#Disssolve
printstring          =  current_buffer_temp[80:]
print "--- Dissolving : [..]%s" % printstring
print "--- (This is a long process...)"


print "Normal DISSOLVE"

arcpy.Dissolve_management(visual_buffer_temp, visual_buffer,"","","SINGLE_PART","")

#dec_dissolve(visual_buffer_temp, visual_buffer,1000)


# Calculate area for the visual buffer and clean up
arcpy.Delete_management(visual_buffer_temp)
arcpy.CalculateAreas_stats(visual_buffer, visual_buffer_temp)
arcpy.Delete_management(visual_buffer)
arcpy.Copy_management(visual_buffer_temp, visual_buffer)
arcpy.Delete_management(visual_buffer_temp)
arcpy.DefineProjection_management(visual_buffer, projectionfile)


# Add some fields for the visual buffer:
# - index number
arcpy.AddField_management(visual_buffer, "z_nr",     "LONG",  "9",  "", "", "z_nr",      "NULLABLE", "REQUIRED")

# - name field
arcpy.AddField_management(visual_buffer, "sonenavn", "TEXT",  "10", "", "", "sonenavn",  "NULLABLE", "REQUIRED")

# - Zone area (area covered by this zone
arcpy.AddField_management(visual_buffer, "z_area",   "FLOAT", "12", "", "", "z_area",    "NULLABLE", "REQUIRED")

# - Total islands in zone
arcpy.AddField_management(visual_buffer, "z_islnr",  "FLOAT", "12", "", "", "z_islnr",   "NULLABLE", "REQUIRED")

# - Total island area
arcpy.AddField_management(visual_buffer, "i_area",   "FLOAT", "12", "", "", "i_area",    "NULLABLE", "REQUIRED")

# - Total islands
arcpy.AddField_management(visual_buffer, "i_perim",  "FLOAT", "12", "", "", "i_perim",   "NULLABLE", "REQUIRED")

#A - Add field for distance to shore
arcpy.AddField_management(visual_buffer, "i_mindist",   "LONG", "12", "", "", "isl_land_d","NULLABLE", "REQUIRED")

# Update is_lev_# value with 1
rows = arcpy.UpdateCursor(visual_buffer)


# Move current area from F_AREA (don't like capitals) to z_area and delete former.
# Also set the zone number.
print "-- Update values."


to_file               += " Arealinformasjon per sone angitt i dekar\n"

count=1
for row in rows:

    new_area = int((row.getValue("F_AREA")))

    row.setValue("z_area",(new_area/1000))

    row.setValue("z_nr",count)

    rows.updateRow(row)


    to_file               += "\n"
    to_file               += "   %s: %s \n" % (count, new_area/1000)


    count+=1


arcpy.DeleteField_management(visual_buffer, "F_AREA")

del rows
del row




#create the coastline risk zone - too early?
buffer_outer        = "%sbuffer_%s.shp"                % (path_maps_process,i-1)
coastal_line_risk   = "%sf_%s_coastal_riskline.shp"    % (path_maps_result,county_nr)

arcpy.Intersect_analysis([[buffer_outer,1], [coastline,2]], coastal_line_risk, "ALL", "", "LINE")



# Calculate area and perimeter for islands within each visual buffer areas


# Update is_lev_# value with 1
rows = arcpy.UpdateCursor(visual_buffer)

print "-- Iterating for value updates"


to_file               += "\n"
to_file               += "\n"
to_file               += "\n"
to_file               += " Informasjon om øyer i de enkelte sonene\n"
to_file               += "\n"

current_id = 0

for row in rows:


    print "--- Iteration #%s" % (current_id)

    visual_buffer_temp      = "%svisual_buffer_temp.shp" % (path_maps_process)

    zone_islands_nocalc     = "%szone_islands_nocalc.shp" % (path_maps_process)

    zone_islands_areacalc   = "%szone_islands_areacalc.shp" % (path_maps_process)

    current_id              = row.getValue("FID")

    evaluationstring        = "\"FID\" = %s" % (current_id)


    arcpy.Select_analysis(visual_buffer, visual_buffer_temp, evaluationstring)


    # intersect temporary buffer with one islands
    arcpy.Intersect_analysis ([[islands_all, 1], [visual_buffer_temp,2]], zone_islands_nocalc, "ALL", "", "")
    arcpy.DefineProjection_management(zone_islands_nocalc, projectionfile)


    # Calculate area for the islands within one of the buffer zones
    print "---- Initiating zone level area stats"
    arcpy.CalculateAreas_stats(zone_islands_nocalc, zone_islands_areacalc)


    # Calculate perimeter for the islands within one of the buffer zones
    print "---- Initiating izone level slands total perimeter calculation"
    arcpy.CalculateField_management(zone_islands_areacalc, 'i_perim', '!shape.length@meters!', 'PYTHON')


    # Calculate distance from any islands within the zone to shore for.
    # The resulting value is used as update to the

    print "---- Initiating distance to shore calculation"
    #arcpy.Near_analysis(zone_islands_areacalc,coastal_line_risk)


    print "---- Iterating through value updates with some tests"
    #Do the area calculation and set the value for eac island selected within one of the buffers
    rows_area = arcpy.UpdateCursor(zone_islands_areacalc)

    mindistance   = 10000000
    totalarea     = 0
    totalperim    = 0
    count_islands = 0

    for row_area in rows_area:

        new_area          = row_area.getValue("F_AREA")
        totalarea_temp    = totalarea
        totalarea         = new_area + totalarea_temp


        new_perim         = row_area.getValue("i_perim")
        totalperim_temp   = totalperim
        totalperim        = new_perim + totalperim_temp

        current_distance  = 0

        #int(row_area.getValue("NEAR_DIST"))

        if (current_distance < mindistance):
            mindistance = current_distance


        count_islands +=1

    row.setValue("i_area",(totalarea/1000))

    row.setValue("i_perim",totalperim)

    row.setValue("z_islnr",count_islands)

    row.setValue("i_mindist",mindistance)


    to_file               += " %s \n" % (current_id+1)
    to_file               += "    Antall øyer          : %s \n" % (count_islands)
    to_file               += "    Øyenes areal   (da)  : %s \n" % (int(totalarea/1000))
    to_file               += "    Øyenes omkrets (m)   : %s \n" % (int(totalperim))
    to_file               += "    Nærmest fastlandet   : %s \n\n\n" % (mindistance)


    rows.updateRow(row)

    print "--- Calculated @#%s: Islands %s, Perim %s, distance to shore %s" % (current_id, count_islands, totalperim, current_distance)


    del row_area
    del rows_area

    # clean up
    arcpy.Delete_management(zone_islands_areacalc)
    arcpy.Delete_management(visual_buffer_temp)
    arcpy.Delete_management(zone_islands_nocalc)


    current_id +=1


del row
del rows


run_time_end    = strftime("%d/%m/%Y  %H:%M:%S", localtime())

to_file        += "Kjøringen sluttet   : %s \n" % (run_time_end)


print to_file

loggfile = "%sberegningslogg.txt" % (path_maps_result)

current_file    = open(loggfile, 'w')

current_file.write(to_file)

current_file.closed



################################################################
# We now have a folder with expanding buffers named sislands_buffer_join_[n].shp
# The bigger the areas covered the more they will bleed together
#