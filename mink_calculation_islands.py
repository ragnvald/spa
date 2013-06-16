
# ---------------------------------------------------------------------------
# mink_calculation_islands.py
#
# This script calculates potential areas for figting alien species
# in coastal areas. It looks at clustered islands and their (naerhet)
# Based on this natural clusters will be found. Their closeness to
# the shoreline is also visualized.
#
# Delivered as-is. If it works - fine for you. If it fails - too bad.
# No are given guarantees whatsoever. If you use this program for
# illegal purposes - don't blame me.
#
# License type is GNU GPL. Copy, distribute and change freely. Keep
# the author in mind for crediting. Come to think of it, use this
# reference:
#
# Input:         * your_islands.shp
#                * your_protected_areas.shp
#                * your_projection_file.prj
#
#
# Output:        * visual_zones.shp
#                * coastline_riskzone.shp
#
# Prerequisites: * The ESRI ArcPy library
#
# ---------------------------------------------------------------------------



################################################################
#
# Import modules

import arcpy, os
from datetime import datetime,date,time
from time import gmtime, strftime, localtime
from mink_lib import *



################################################################
#
# Define variables

startTime = datetime.now()

person_responsible            = "CK"

#Add your own path here
path_project                  = "C:/Users/RAGLAR/Desktop/GitHub/spa/calculation_demo/"

path_basis                    = "%smaps_basis/"   % (path_project)
path_process                  = "%smaps_process/" % (path_project)
path_result                   = "%smaps_result/"  % (path_project)

to_log                        = ""
log_file                      = "log.txt"

list_buffer_distance_m        = 2000
max_distancetoshore_possible  = 200000
i                             = 1

area_name                     = "nordland"

file_projection               = "%swgs84_utm_33n.prj" % (path_basis)
file_coastline                = "%scoastline.shp" % (path_basis)
file_islandsall               = "%sislands.shp" % (path_basis)
file_areasprotected           = "%sareasprotected.shp" % (path_basis)

run_time_start                = strftime("%d/%m/%Y  %H:%M:%S", localtime())





################################################################
#
# Information to log

to_log               += "Calculation of zones suitable for decimation of american mink\n"
to_log               += "#############################################################\n\n\n"
to_log               += " Calculation started   : %s \n\n\n" % (run_time_start)
to_log               += "\n"
to_log               += "\n"
to_log               += " Basis for this calculation:\n"
to_log               += "\n"
to_log               += "\n"
to_log               += "\n"
to_log               += " Responsible              : %s" % (person_responsible)
to_log               += "\n"
to_log               += "\n"
to_log               += " Buffer distance (meters) : %s \n" % (list_buffer_distance_m)
to_log               += "\n"
to_log               += " Areaname                 : %s  \n" % (area_name)
to_log               += "\n"
to_log               += " Projection               : %s\n" % (file_projection)
to_log               += "\n"
to_log               += " Coastline: %s\n" % (file_coastline)
to_log               += "\n"
to_log               += " Islands file: %s\n" % (file_islandsall)
to_log               += "\n"

handle_log(to_log,path_result,log_file)
to_log     = ""



################################################################
#
# Information to log

number_islands_tostartwith = int(str(arcpy.GetCount_management(file_islandsall)))
islands_affected_total      = "%sislands_affected_total.shp" % (path_result)

to_log               += " Number of islands in this calculation: %s\n" % (number_islands_tostartwith)
to_log               += "\n"

handle_log(to_log,path_result,log_file)
to_log     = ""


islands_affected_total_nopath = "islands_affected_total.shp"

arcpy.CreateFeatureclass_management(path_result, islands_affected_total_nopath, "POLYGON")
arcpy.DefineProjection_management(islands_affected_total, file_projection)

islands_affected_total_temp = "%sislands_affected_total_temp.shp" % (path_process)
islands_left                = "%sislands_left.shp" % (path_process)

# Copy all islands to process folder where a file will keep all
# files not affected by the evaluation. Through our calculation
# we will remove islands from this file until our iterations has
# run throughout


arcpy.Copy_management(file_islandsall, islands_left)

arcpy.DefineProjection_management(islands_left, file_projection)


# Join the protected areas with the islands. Our target objects
# are the islands, so whatever joins we get with the protected
# areas will add up in the Join_Count variable

islands_affected_joined = "%sislands_affected_joined.shp" % (path_process)
arcpy.SpatialJoin_analysis(islands_left, file_areasprotected, islands_affected_joined)


# Select all islands which are overlapped with one or more protected areas.
# Deposit the joins in a new file (islands_affected).

islands_affected     = "%sislands_affected.shp" % (path_process)
where_clause         = '"Join_Count" > 0'
arcpy.Select_analysis(islands_affected_joined, islands_affected, where_clause)


# Clean up: Delete temporary joined file

arcpy.Delete_management(islands_affected_joined)

islands_left_new        = "%sislands_left_new.shp" % (path_process)


# Delete affected islands from our store of non-affected islands
# The file will be used as a basis for later buffering.
#

arcpy.Erase_analysis(islands_left,islands_affected,islands_left_new)
arcpy.Delete_management(islands_left)
arcpy.Copy_management(islands_left_new, islands_left)
arcpy.Delete_management(islands_left_new)

arcpy.DefineProjection_management(islands_left, file_projection)



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

while (number_islands_left < number_islands_left_last):


    starttimeround = datetime.now()


    # Setting up variables
    current_buffer_temp        = "%sbuffer_temp.shp"        % (path_process)

    current_buffer_temp_temp   = "%sbuffer_temp_temp.shp"   % (path_process)

    current_buffer             = "%sbuffer_%s.shp"          % (path_process,i)

    ################################################
    # B U F F E R S
    #
    # Buffer around all islands
    #
    printstring                =  islands_affected[80:]

    distanceField              = "%s Meters" % (list_buffer_distance_m)
    sideType                   = ""
    endType                    = ""
    dissolveType               = "NONE"
    dissolveField              = ""

    arcpy.Buffer_analysis(islands_affected, current_buffer_temp, distanceField, sideType, endType, dissolveType, dissolveField)

    arcpy.DefineProjection_management(current_buffer_temp, file_projection)

    if i>1:

        # If this is not the first buffer the older buffer is merged with the new buffer
        # This way we will get a full coverage buffer under all hitherto affected islands

        formeriterator   = i-1

        formerbuffer     = "%sbuffer_%s.shp"          % (path_process,formeriterator)

        arcpy.Merge_management([formerbuffer,current_buffer_temp], current_buffer_temp_temp)
        arcpy.Delete_management(current_buffer_temp)

        arcpy.Copy_management(current_buffer_temp_temp, current_buffer_temp)
        arcpy.Delete_management(current_buffer_temp_temp)





    #Repair the geometries made by ESRI.
    arcpy.RepairGeometry_management(current_buffer_temp, "Keep_NULL")

    group_dissolve(current_buffer_temp, current_buffer,80,path_process)

    #arcpy.Dissolve_management(current_buffer_temp, current_buffer,"","","SINGLE_PART","")

    arcpy.DefineProjection_management(current_buffer, file_projection)


    arcpy.Delete_management(current_buffer_temp)


    # Add relative field for affected islands
    fieldname = "islev_%s" % (i)
    arcpy.AddField_management(current_buffer,fieldname,"LONG", 9, "", "","","NULLABLE")

    # Update is_lev_# value with 1
    rows = arcpy.UpdateCursor(current_buffer)
    for row in rows:
        row.setValue(fieldname,"1")
        rows.updateRow(row)



    arcpy.SpatialJoin_analysis(islands_left, current_buffer, islands_affected_joined)



    ################################################################
    #Select all islands with more than one protected area status and make a new layer
    #

    islands_affected        = "%sislands_affected_%s.shp" % (path_process,i)
    where_clause ='"Join_Count" > 0'
    arcpy.Select_analysis(islands_affected_joined, islands_affected, where_clause)
    arcpy.DefineProjection_management(islands_affected, file_projection)


    # Clean up: Delete temporary joined file
    arcpy.Delete_management(islands_affected_joined)

    # add identification field to the islands affected
    fieldname = "isl_lev"
    arcpy.AddField_management(islands_affected,fieldname,"LONG", 9, "", "","","NULLABLE")

    rows = arcpy.UpdateCursor(islands_affected)

    for row in rows:

        row.setValue("isl_lev",i)
        rows.updateRow(row)


    # Add the new islands to the original one
    arcpy.Merge_management([islands_affected_total, islands_affected], islands_affected_total_temp)
    arcpy.Delete_management(islands_affected_total)
    arcpy.Copy_management(islands_affected_total_temp, islands_affected_total)
    arcpy.Delete_management(islands_affected_total_temp)


    # Delete affected islands from islands_left
    arcpy.Erase_analysis(islands_left,islands_affected,islands_left_new)
    arcpy.Delete_management(islands_left)
    arcpy.Copy_management(islands_left_new, islands_left)
    arcpy.Delete_management(islands_left_new)

    timestamp = (datetime.now()-starttimeround)


    #remove all islands within a buffer of n meters away from the coastline

    number_islands_left_last = number_islands_left
    number_islands_left = int(str(arcpy.GetCount_management(islands_left)))

    i+=1


# union for all buffers affected


# write to file
to_log += " Number of islands not in any of the eradication zones are: %s" % number_islands_left
to_log               += "\n"
to_log               += "\n"

handle_log(to_log,path_result,log_file)
to_log     = ""

#Start counting again
starttimeround = datetime.now()

count=1

unionlist=""

# Merging (union) between all buffer objects

while count < i:

    unionobject   = "%sbuffer_%s.shp" % (path_process,count)

    if count>1:
        unionlist = unionlist + ";" + unionobject
    else:
        unionlist = unionobject


    count+=1


full_buffer_temp  = "%sfullbuffer_temp.shp"   % (path_process)

arcpy.Union_analysis(unionlist,full_buffer_temp)


# Add a field in the buffer to keep summarized values
fieldname = "isl_lev"
arcpy.AddField_management(full_buffer_temp,fieldname,"LONG", 9, "", "","","NULLABLE")

count=1


# Update is_lev_# value with 1

rows = arcpy.UpdateCursor(full_buffer_temp)


# Adding island level (isl_lev) to the buffer based on respective buffer level values.

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

islands_infested     = "%sislands_in_zones.shp" % (path_result)

islands_affected     = "%sislands_affected.shp" % (path_process)


arcpy.Merge_management([islands_affected,islands_affected_total], islands_infested)
arcpy.DefineProjection_management(islands_infested, file_projection)


#buffer around all islands
eradication_zone_temp   = "%seradication_zone_temp.shp" % (path_process)


eradication_zone        = "%seradication_zone.shp" % (path_result)


# the visual buffer should be half of the total potential swimming distance

distanceField        = "%s Meters" % (list_buffer_distance_m/2)
sideType             = ""
endType              = ""
dissolveType         = "NONE"
dissolveField        = ""
arcpy.Buffer_analysis(islands_infested, eradication_zone_temp, distanceField, sideType, endType, dissolveType, dissolveField)


#Disssolve

group_dissolve(eradication_zone_temp, eradication_zone,80,path_process)


# Calculate area for the visual buffer and clean up
arcpy.Delete_management(eradication_zone_temp)
arcpy.CalculateAreas_stats(eradication_zone, eradication_zone_temp)
arcpy.Delete_management(eradication_zone)
arcpy.Copy_management(eradication_zone_temp, eradication_zone)
arcpy.Delete_management(eradication_zone_temp)
arcpy.DefineProjection_management(eradication_zone, file_projection)


# Add some fields for the visual buffer:
# - index number
arcpy.AddField_management(eradication_zone, "z_nr",     "LONG",  "9",  "", "", "z_nr",      "NULLABLE", "REQUIRED")

# - Zone area (area covered by this zone
arcpy.AddField_management(eradication_zone, "z_area",   "FLOAT", "12", "", "", "z_area",    "NULLABLE", "REQUIRED")

# - Total islands in zone
arcpy.AddField_management(eradication_zone, "z_islnr",  "FLOAT", "12", "", "", "z_islnr",   "NULLABLE", "REQUIRED")

# - Total island area
arcpy.AddField_management(eradication_zone, "i_area",   "FLOAT", "12", "", "", "i_area",    "NULLABLE", "REQUIRED")

# - Total islands
arcpy.AddField_management(eradication_zone, "i_perim",  "FLOAT", "12", "", "", "i_perim",   "NULLABLE", "REQUIRED")

# Update is_lev_# value with 1
rows = arcpy.UpdateCursor(eradication_zone)


# Move current area from F_AREA (don't like capitals) to z_area and delete former.
# Also set the zone number.

to_log               += " Area information per zone (da)\n"

handle_log(to_log,path_result,log_file)
to_log     = ""

count=1
for row in rows:

    new_area = int((row.getValue("F_AREA")))

    row.setValue("z_area",(new_area/1000))

    row.setValue("z_nr",count)

    rows.updateRow(row)

    to_log               += "   %s: %s \n" % (count, new_area/1000)

    handle_log(to_log,path_result,log_file)
    to_log     = ""


    count+=1


arcpy.DeleteField_management(eradication_zone, "F_AREA")

del rows
del row






# Calculate area and perimeter for islands within each visual buffer areas


# Update is_lev_# value with 1
rows = arcpy.UpdateCursor(eradication_zone)

to_log               += "\n"
to_log               += "\n"
to_log               += "\n"
to_log               += " Information about islands in the respecctive zones\n"
to_log               += "\n"

handle_log(to_log,path_result,log_file)
to_log     = ""

current_id = 0

for row in rows:

    eradication_zone_temp      = "%seradication_zone_temp.shp" % (path_process)

    zone_islands_nocalc     = "%szone_islands_nocalc.shp" % (path_process)

    zone_islands_areacalc   = "%szone_islands_areacalc.shp" % (path_process)

    current_id              = row.getValue("FID")

    evaluationstring        = "\"FID\" = %s" % (current_id)


    arcpy.Select_analysis(eradication_zone, eradication_zone_temp, evaluationstring)


    # intersect temporary buffer with one islands
    arcpy.Intersect_analysis ([[file_islandsall, 1], [eradication_zone_temp,2]], zone_islands_nocalc, "ALL", "", "")
    arcpy.DefineProjection_management(zone_islands_nocalc, file_projection)


    # Calculate area for the islands within one of the buffer zones

    arcpy.CalculateAreas_stats(zone_islands_nocalc, zone_islands_areacalc)


    # Calculate perimeter for the islands within one of the buffer zones

    arcpy.CalculateField_management(zone_islands_areacalc, 'i_perim', '!shape.length@meters!', 'PYTHON')


    # Calculate distance from any islands within the zone to shore for.
    # The resulting value is used as update to the


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

        count_islands +=1

    row.setValue("i_area",(totalarea/1000))

    row.setValue("i_perim",totalperim)

    row.setValue("z_islnr",count_islands)


    to_log               += " %s \n" % (current_id+1)
    to_log               += "    Number of islands     : %s \n" % (count_islands)
    to_log               += "    Islands area     (da) : %s \n" % (int(totalarea/1000))
    to_log               += "    Islands perimeter (m) : %s \n" % (int(totalperim))
    to_log               += "    Closest mainland  (m) : %s \n\n\n" % (mindistance)

    handle_log(to_log,path_result,log_file)
    to_log     = ""

    rows.updateRow(row)


    del row_area
    del rows_area

    # clean up
    arcpy.Delete_management(zone_islands_areacalc)
    arcpy.Delete_management(eradication_zone_temp)
    arcpy.Delete_management(zone_islands_nocalc)

    current_id +=1


del row
del rows


##############################################################################################
#
# Create the coastline risk zone based on an extended buffer outside the published buffer
#
buffer_outer                   = "%seradication_zone.shp"      % (path_result)

distanceField                  = "%s meters" % (int(list_buffer_distance_m/2))
sideType                       = ""
endType                        = ""
dissolveType                   = "NONE"
dissolveField                  = ""
buffer_outer_extra   = "%seradication_zone_ekstra.shp" % (path_process)
arcpy.Buffer_analysis(buffer_outer, buffer_outer_extra, distanceField, sideType, endType, dissolveType, dissolveField)


# Intersect between the buffer and the coastline gives us the risk zone.
coastal_line_risk   = "%scoastal_riskline.shp"    % (path_result)
arcpy.Intersect_analysis([[buffer_outer_extra,1], [file_coastline,2]], coastal_line_risk, "ALL", "", "LINE")


#
run_time_end    = strftime("%d/%m/%Y  %H:%M:%S", localtime())

to_log        += "Calculations ended : %s \n" % (run_time_end)
handle_log(to_log,path_result,log_file)

print "Calculation concluded"