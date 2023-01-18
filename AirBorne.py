from __future__ import print_function
import time
from turtle import home
from dronekit import connect, VehicleMode, LocationGlobalRelative
import sys
import argparse
import math
import datetime
import pandas as pd

######### Drone Hardware Parameters ###########
airspeed = 1                                                 #int(input("Enter the Desired Air Speed in meter/second : "))
BatteyCapacity = 2200                                         #int(input("Enter Battery capacity in mAh : "))
altitude = 5                                                 #int(input("Enter fligt Altitude for the misson : "))
takeOffWeight = 1192                                          #int(input("Enter Takeoff Weight of The Drone : "))
maxThrust = 600                                               #int(input("Enter max Thrust per motor : "))
maxCurrent = 17.41
###############################################
#_---------------------------------------------------------------------  MATH. EQ ----------------------------------------------------------------------------------------------------------
def totalDistanceCalculated(lat_list,lon_list):
    FinalDist=0
    for i in range(len(lat_list)-1):
        FinalDist = FinalDist + getDistanceInMeters(lat_list[i],lon_list[i],lat_list[i+1],lon_list[i+1])
    FinalDist = FinalDist + getDistanceInMeters(lat_list[-1],lon_list[-1],lat_list[0],lon_list[0])
    return int(FinalDist+1)

def getDistanceInMeters(Location1_lat,Location1_lon, Location2_lat,Location2_lon):
    dlat = Location2_lat - Location1_lat
    dlong = Location2_lon - Location1_lon
    ourValue = math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
    return (ourValue) - ((ourValue/100)*4.83333)  # offset

#_-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight):
    #totalTime=30
    BatteyCapacity = BatteyCapacity/1000  #changing mAh to Ah
    batteryDischarge = BatteyCapacity*0.8
    thrustPer1Amp = maxThrust/maxCurrent
    avgAmpDraw = (takeOffWeight/thrustPer1Amp) #Thrust for 1 Ampere of current
    totalTime = round(((batteryDischarge/avgAmpDraw)*60),4)  # Total Flight Time
    return totalTime

def flightTimeCurrent(dist,airspeed):    #missonFlightTime
    return((dist/airspeed)/60)

def flightTimeCustomer(module,lat_list,lon_list,airspeed):
    customerFinalDistance = 0
    for i in range(len(lat_list)-1):
        customerFinalDistance = customerFinalDistance + getDistanceInMeters(lat_list[i],lon_list[i],lat_list[i+1],lon_list[i+1])
    if module == 1:
        customerFlightTime = customerFinalDistance/airspeed
        return int((customerFlightTime+1)/60)
    else:
        customerFlightTime = customerFinalDistance/airspeed
        return int((customerFlightTime+31)/60)
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def coordinatesLists(location_list,lat_list,lon_list):    #    
        for i in location_list:
            i = str(i)
            i = i.replace('(','')
            i = i.replace(')','')
            i = i.split(",")

            lat_list.append(float(i[0]))
            try:
                lon_list.append(float(i[1]))
            except:
                print('Error in coordinates entered')

def connectMyCopter():
        parser = argparse.ArgumentParser(description='commands')
        parser.add_argument('--connect')
        args = parser.parse_args()

        connection_string = args.connect
        baud_rate = 57400

        vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
        return vehicle

def batteryLevel():
    print(" Battery: %s" % vehicle.battery)      
    if vehicle.battery.voltage <= 11.18:
        print("Battery is below 20%, Drone cannot fly!")
        print(vehicle.battery)
        while True:
            if vehicle.location.global_relative_frame.alt < 0.3 :
                print("Vehicle Landed")
                # time.sleep(1)
                break
            time.sleep(1)
        time.sleep(30)
        vehicle.close()
        sys.exit() 

def arm_and_takeoff(aTargetAltitude):
        # print("VEHICLE = %s"%vehicle)
        while not vehicle.is_armable:
            print("Waiting for vehicle to become armable")
            time.sleep(1)
        
        vehicle.mode = VehicleMode("GUIDED")
        # while vehicle.mode != "GUIDED":
        #     print("Waiting for vehicle to enter GUIDED mode")
        #     time.sleep(1)

        vehicle.armed = True
        while vehicle.armed ==False:
            print("Waiting for vehicle to become armed")
            time.sleep(1)
        print("ARMED!!!")
        vehicle.simple_takeoff(aTargetAltitude)

        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("=> Reached target altitude = ", vehicle.location.global_relative_frame.alt)
                break
            time.sleep(1)
            
        batteryLevel() 
        
        print("-------------------")
        print(vehicle.velocity)
        print("-------------------")
        print(vehicle.heading)
        print("-------------------")
        print(vehicle.mode.name)
        print("-------------------")
        print(vehicle.last_heartbeat)
        print("-------------------")
        print(vehicle.rangefinder)
        print("-------------------")
        print(vehicle.rangefinder.distance)
        print("-------------------")
        print(vehicle.rangefinder.voltage)
        print("-------------------")
        print(vehicle.ekf_ok)
        print("-------------------")
        print(vehicle.groundspeed)
        print("-------------------")
        print(vehicle.airspeed)
        print("-------------------")
        print(vehicle.capabilities.ftp)

        return None
    
vehicle = connectMyCopter()
print("About to takeoff...")

def EndToEnd():
    location_count = 2
    location_list = []
    lat_list = []
    lon_list = []

    loc_home = str(vehicle.location.global_frame.lat)+','+str(vehicle.location.global_frame.lon)
    location_list.append(loc_home)
    
    for i in range(location_count):
            if i == 0:
                location_list.append(input("Enter Partner location Coordinates : ")) # 21.150481963525785,79.04314168998563
            else:
                location_list.append(input("Enter Destination location Coordinates : ")) # 21.148231357586596, 79.04460332303546

    coordinatesLists(location_list, lat_list, lon_list)
    
    #vehicle.mode = VehicleMode("STABILIZE")
    # home_lat = vehicle.location.global_frame.lat  # home location 
    # home_long = vehicle.location.global_frame.lon
    # home = LocationGlobalRelative(home_lat, home_long, 3)
    # print(home_lat, home_long)
    ######################## Going to Partner #########################################
    # lat = 21.148127783671477 # 21.148127783671477, 79.04118915312793
    # long = 79.04118915312793
    
    if int(totalDistanceCalculated(lat_list, lon_list) > ((totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight)*airspeed)*60)):
        vehicle.close()
        print((totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight)*airspeed)*60)
        print(totalDistanceCalculated(lat_list, lon_list))
        print("Mission out of bound [Reduce distance between base Station and Consumer]")
        sys.exit()
    elif(flightTimeCurrent(totalDistanceCalculated(lat_list,lon_list),airspeed) > (totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight))):
        vehicle.close()
        print("Mission out of bound [Flight time too High]")
        sys.exit()
    else:
        print("Your Delivery is expected in : "+str(flightTimeCustomer(module,lat_list,lon_list,airspeed))+" mins")
        time.sleep(1)
 
        # Timer Starts !
        timerStart = datetime.datetime.now()
        
        timeList = []
        arm_and_takeoff(10)
        destination = LocationGlobalRelative(lat_list[1], lon_list[1], 10)   #latitude, long, altitude
        batteryLevel()
        vehicle.simple_goto(destination)
        ##############################################################################################
        print("-------------------")
        print(vehicle.velocity)
        print("-------------------")
        print(vehicle.heading)
        print("-------------------")
        print(vehicle.mode.name)
        print("-------------------")
        print(vehicle.last_heartbeat)
        print("-------------------")
        print(vehicle.rangefinder)
        print("-------------------")
        print(vehicle.rangefinder.distance)
        print("-------------------")
        print(vehicle.rangefinder.voltage)
        print("-------------------")
        print(vehicle.ekf_ok)
        print("-------------------")
        print(vehicle.groundspeed)
        print("-------------------")
        print(vehicle.airspeed)
        print("-------------------")
        print(vehicle.capabilities.ftp)
        ##############################################################################################
        while round(vehicle.location.global_frame.lat,5) != round(lat_list[1],5) and  round(vehicle.location.global_frame.lon,5) != round(lon_list[1],5):
            time.sleep(1)
            print("Velocity: %s" % vehicle.velocity)
        print("Partner Reached")
        vehicle.mode = VehicleMode("LAND")
        
        while True:
            if vehicle.location.global_relative_frame.alt < 0.3 :
                print("Vehicle Landed")
                # time.sleep(1)
                break
            time.sleep(1)
        time.sleep(30)
        timeList.append(datetime.datetime.now())
        ################################ Going to Customer #########################################
        arm_and_takeoff(10)
        # lat_2 = 21.148739436072805
        # long_2 = 79.044802086102
        destination_2 = LocationGlobalRelative(lat_list[2], lon_list[2], 10)
        batteryLevel()
        vehicle.simple_goto(destination_2)
        ##############################################################################################
        print("-------------------")
        print(vehicle.velocity)
        print("-------------------")
        print(vehicle.heading)
        print("-------------------")
        print(vehicle.mode.name)
        print("-------------------")
        print(vehicle.last_heartbeat)
        print("-------------------")
        print(vehicle.rangefinder)
        print("-------------------")
        print(vehicle.rangefinder.distance)
        print("-------------------")
        print(vehicle.rangefinder.voltage)
        print("-------------------")
        print(vehicle.ekf_ok)
        print("-------------------")
        print(vehicle.groundspeed)
        print("-------------------")
        print(vehicle.airspeed)
        print("-------------------")
        print(vehicle.capabilities.ftp)
        ##############################################################################################
        while round(vehicle.location.global_frame.lat,5) != round(lat_list[2],5) and  round(vehicle.location.global_frame.lon,5) != round(lon_list[2],5):
            time.sleep(1)
        print("Customer Reached")
        vehicle.mode = VehicleMode("LAND")
        timeList.append(datetime.datetime.now())
        time.sleep(30)
        timeList.append(datetime.datetime.now())
        ################################ Going to home #################################################
        arm_and_takeoff(10)
        home = LocationGlobalRelative(lat_list[0], lon_list[0], 10)
        batteryLevel()
        vehicle.simple_goto(home)
        ##############################################################################################
        print("-------------------")
        print(vehicle.velocity)
        print("-------------------")
        print(vehicle.heading)
        print("-------------------")
        print(vehicle.mode.name)
        print("-------------------")
        print(vehicle.last_heartbeat)
        print("-------------------")
        print(vehicle.rangefinder)
        print("-------------------")
        print(vehicle.rangefinder.distance)
        print("-------------------")
        print(vehicle.rangefinder.voltage)
        print("-------------------")
        print(vehicle.ekf_ok)
        print("-------------------")
        print(vehicle.groundspeed)
        print("-------------------")
        print(vehicle.airspeed)
        print("-------------------")
        print(vehicle.capabilities.ftp)
        ##############################################################################################
        while round(vehicle.location.global_frame.lat,5) != round(lat_list[0],5) and  round(vehicle.location.global_frame.lon,5) != round(lon_list[0],5):
            time.sleep(1)
        print("Home Reached")
        vehicle.mode = VehicleMode("LAND")
        time.sleep(30)
        timerEnd = datetime.datetime.now()
        # print((timeList[1]-timeList[0]), "Actual Time Taken")

        # Customer flight time
        custFlightTimeActual = timeList[1]  # actual flight time calclated for customer
        custFlightTimeActual = pd.to_datetime(custFlightTimeActual)
        custFlightTimeActual = custFlightTimeActual - timerStart
        custFlightTimeActualInMins = str(round(float(custFlightTimeActual.total_seconds()/60),3))
        # Partner flight time
        partnerFlightTimeActual = timeList[0]  # actual flight time calclated for customer
        partnerFlightTimeActual = pd.to_datetime(partnerFlightTimeActual)
        partnerFlightTimeActual = partnerFlightTimeActual - timerStart
        partnerFlightTimeActualInMins = str(round(float(partnerFlightTimeActual.total_seconds()/60),3))      
        #timer Ends
        
        
        print("End of function")
        missionTime = timerEnd - timerStart
        missionTimeInMinutes = str(round(float(missionTime.total_seconds()/60),3))
        
        print("Mission took: "+ missionTimeInMinutes + " mins")
        print("Your Delivery took: "+custFlightTimeActualInMins+" mins.")
        print("Time taken to reach Partner Location: "+partnerFlightTimeActualInMins+" mins")
        
        print("Mission Complete")
        print("--------------------------------------------------------------------")
        print("\t\t\t  Do you want to fly with Airborne again?")
        moduleSelectforEndToEnd = int(input("\t\t\t\tPress 1 for Integrated Module \n\t\t\t\tPress 2 For End to End module\n\t\t\t\tPress 3 to close the current session\n\t\t\t"))
        print("--------------------------------------------------------------------")
        if moduleSelectforEndToEnd == 1:
            Integrated()
        elif moduleSelectforEndToEnd == 2:
            EndToEnd()
        elif moduleSelectforEndToEnd == 3:
            vehicle.close()
            print("Mission Complete")
            sys.exit()

def Integrated():
    location_count = 1
    location_list = []
    lat_list = []
    lon_list = []

    loc_home = str(vehicle.location.global_frame.lat)+','+str(vehicle.location.global_frame.lon)
    location_list.append(loc_home)
    
    for i in range(location_count):
        location_list.append(input("Enter Your Location : "))
    print("Base Station Location: ", loc_home + ", Current Time: ",datetime.datetime.now())
    coordinatesLists(location_list, lat_list, lon_list)
    #vehicle.mode = VehicleMode("STABILIZE")
    # home_lat = vehicle.location.global_frame.lat  # home location 
    # home_long = vehicle.location.global_frame.lon
    # home = LocationGlobalRelative(home_lat, home_long, 3)
    # print(home_lat, home_long)
    
    # lat = 21.148127783671477 # 21.148127783671477, 79.04118915312793
    # long = 79.04118915312793
    if int(totalDistanceCalculated(lat_list, lon_list) > ((totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight)*airspeed)*60)):
        vehicle.close()
        print((totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight)*airspeed)*60)
        print(totalDistanceCalculated(lat_list, lon_list))
        print("Mission out of bound [Reduce distance between base Station and Consumer]")
        sys.exit()
    elif(flightTimeCurrent(totalDistanceCalculated(lat_list,lon_list),airspeed) > (totalFlightTime(BatteyCapacity,maxThrust,maxCurrent,takeOffWeight))):
        vehicle.close()
        print("Mission out of bound [Flight time too High]")
        sys.exit()
    else:
        print("Your Delivery is expected in : "+str(flightTimeCustomer(module,lat_list,lon_list,airspeed))+" mins")
        time.sleep(1)
        
######################## Going to Customer #################################################
    # Timer Starts !
    timerStart = datetime.datetime.now()
    
    timeList = []
    arm_and_takeoff(3)
    destination = LocationGlobalRelative(lat_list[1], lon_list[1], 7)   #latitude, long, altitude
    batteryLevel()
    vehicle.simple_goto(destination)
    ##############################################################################################
    print("-------------------")
    print(vehicle.velocity)
    print("-------------------")
    print(vehicle.heading)
    print("-------------------")
    print(vehicle.mode.name)
    print("-------------------")
    print(vehicle.last_heartbeat)
    print("-------------------")
    print(vehicle.rangefinder)
    print("-------------------")
    print(vehicle.rangefinder.distance)
    print("-------------------")
    print(vehicle.rangefinder.voltage)
    print("-------------------")
    print(vehicle.ekf_ok)
    print("-------------------")
    print(vehicle.groundspeed)
    print("-------------------")
    print(vehicle.airspeed)
    print("-------------------")
    print(vehicle.capabilities.ftp)
    ##############################################################################################
    while round(vehicle.location.global_frame.lat,5) != round(lat_list[1],5) and  round(vehicle.location.global_frame.lon,5) != round(lon_list[1],5):
        time.sleep(1)
    print("Customer Reached")
    vehicle.mode = VehicleMode("LAND")
    time.sleep(15)
    timeList.append(datetime.datetime.now())

    ################################ Going to home #################################################
    arm_and_takeoff(3)
    home = LocationGlobalRelative(lat_list[0], lon_list[0], 7)   #latitude, long, altitude
    batteryLevel()
    vehicle.simple_goto(home)
    ##############################################################################################
    print("-------------------")
    print(vehicle.velocity)
    print("-------------------")
    print(vehicle.heading)
    print("-------------------")
    print(vehicle.mode.name)
    print("-------------------")
    print(vehicle.last_heartbeat)
    print("-------------------")
    print(vehicle.rangefinder)
    print("-------------------")
    print(vehicle.rangefinder.distance)
    print("-------------------")
    print(vehicle.rangefinder.voltage)
    print("-------------------")
    print(vehicle.ekf_ok)
    print("-------------------")
    print(vehicle.groundspeed)
    print("-------------------")
    print(vehicle.airspeed)
    print("-------------------")
    print(vehicle.capabilities.ftp)
    ##############################################################################################
    while round(vehicle.location.global_frame.lat,5) != round(lat_list[0],5) and  round(vehicle.location.global_frame.lon,5) != round(lon_list[0],5):
        time.sleep(1)
    print("Home Reached")
    vehicle.mode = VehicleMode("LAND")
    time.sleep(2)
    timerEnd = datetime.datetime.now()
        
    custFlightTimeActual = timeList[0]  # actual flight time calclated for customer
    print(custFlightTimeActual)
    # custFlightTimeActual = pd.to_datetime(custFlightTimeActual)
    print(custFlightTimeActual)
    custFlightTimeActual = custFlightTimeActual - timerStart
    print(custFlightTimeActual)
    custFlightTimeActualInMins = str(round(float(custFlightTimeActual.total_seconds()/60),3))
    print(custFlightTimeActualInMins)
    
    missionTime = timerEnd - timerStart
    missionTimeInMinutes = str(round(float(missionTime.total_seconds()/60),3))
    print("Mission took: "+ missionTimeInMinutes + " mins")
    print("Your Delivery took: "+custFlightTimeActualInMins+" mins.")
    print("Mission Complete")
    print(vehicle.battery)
    time.sleep(1)

    print("End of function")
    print("--------------------------------------------------------------------")
    print("\t\t\t  Do you want to fly with Airborne again?")
    moduleSelectforIntegrated = int(input("\t\t\t\tPress 1 for Integrated Module \n\t\t\t\tPress 2 For End to End module\n\t\t\t\tPress 3 to close the current session\n\t\t\t"))
    print("--------------------------------------------------------------------")
    if moduleSelectforIntegrated == 1:
        Integrated()
    elif moduleSelectforIntegrated == 2:
        EndToEnd()
    elif moduleSelectforIntegrated == 3:
        vehicle.close()
        print("Mission Complete")
        sys.exit()

                    ################### INPUTS CONFIGURATIONS  ###################
print("\n\n\n\n\n\n\n\n\n\n\n")  
print("----------------------------------------------------------------------------------------")
print("                          \t     WELCOME TO AIRBORNE\t                                  ")
print("----------------------------------------------------------------------------------------")
print("                \t\tPLEASE SELECT THE DESIRED MODULE\t\t          ")
module = int(input("\t\t\t\tPress 1 for Integrated Module \n\t\t\t\tPress 2 For End to End module\n\t\t\t"))

                    ###################   INPUTS ENDS HERE   ##################
##### MAIN EXECUTION ##### 
while vehicle.mode.name != 'RTL':
    if module == 1:
        Integrated()
    elif module == 2:
        EndToEnd()    
print(vehicle.mode.name)
sys.exit()
