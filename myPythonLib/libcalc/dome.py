import numpy as np 



def calc_azimuth(targetAzi,targetAlt,tube_side,display_report=False):

    def sumsq(vector):
        sum = 0
        for x in vector:
            sum = sum + x*x
        return sum

    output = f"target_azimuth = {targetAzi}   target_altitude = {targetAlt},  tube_side = {tube_side} \n\n"
    dict_tube_side = { "west":1 , "east":0}
    pierSide = dict_tube_side[tube_side]

    latitude = 48.86
    #Offset from dome centre to base mount
    dctbmX = 0
    dctbmY = 0
    dctbmZ = -0.2

    #Offset from base mount to latitude axis
    bmtlaX = -0.11
    bmtlaY = 0
    bmtlaZ = 0.15

    #Distance D from latitude axis to RA/DEC axis intersection
    distD = 0.31

    gemOffset = 0.51
    latOffset = 0

    domeRadius = 1.5
    
    WEST = 1


# STEP 1        
# Get LHA        
    Step1_DEC = np.rad2deg(np.arcsin(np.sin(np.deg2rad(targetAlt))*np.sin(np.deg2rad(latitude))+np.cos(np.deg2rad(targetAlt))*np.cos(np.deg2rad(latitude))*np.cos(np.deg2rad(targetAzi))))
    Step1_angle = np.rad2deg(np.arcsin(-np.sin(np.deg2rad(targetAzi))*np.cos(np.deg2rad(targetAlt))/np.cos(np.deg2rad(Step1_DEC))))
    if ((targetAzi<90) and (targetAzi>=0) or (targetAzi>270) and (targetAzi<360)):
        Step1_LHA = (180-Step1_angle)%360
    else:
        Step1_LHA = (Step1_angle+360)%360
        
    output += f"STEP 1\n[1.1] Declination: {Step1_DEC} degrees\n[1.2] LHA: {Step1_angle} degrees\n[1.3] LHA in correct quadrant: {Step1_LHA} degrees\n\n"

#STEP 2        
#Calculate vector towards target        
#Partial negative version of Honeycutt        
#Vector to target
    Step2_Ac = np.cos(np.deg2rad(targetAlt))*np.cos(np.deg2rad(targetAzi))
    Step2_Bc = -np.cos(np.deg2rad(targetAlt))*np.sin(np.deg2rad(targetAzi))
    Step2_Cc = np.sin(np.deg2rad(targetAlt))
    
    output += f"STEP 2\n[2.1] Ac: {Step2_Ac}\n[2.2] Bc: {Step2_Bc}\n[2.3] Cc: {Step2_Cc}\n\n"

#STEP 3        
#Calculate vector from A to B        
#Honeycutt        
#Vector to centre DEC-axis (no lat-offset)        
    Step3_Ag = -(1-2*(pierSide == WEST))*gemOffset*np.sin(np.deg2rad(Step1_LHA))*np.sin(np.deg2rad(latitude))
    Step3_Bg = -(1-2*(pierSide == WEST))*gemOffset*np.cos(np.deg2rad(Step1_LHA))
    Step3_Cg =  (1-2*(pierSide == WEST))*gemOffset*np.sin(np.deg2rad(Step1_LHA))*np.cos(np.deg2rad(latitude))
    output += f"STEP 3\n[3.1] Ag: {Step3_Ag}\n[3.2] Bg: {Step3_Bg}\n[3.3] Cg: {Step3_Cg}\n\n"

#STEP 4        
#Calculate vector from B to C using lat.offset        
#Rdizzl3
#Vector from DEC axis to centre OTA        
    Step4_At =  (Step2_Bc*Step3_Cg-Step3_Bg*Step2_Cc)/gemOffset*latOffset
    Step4_Bt = -(Step2_Ac*Step3_Cg-Step3_Ag*Step2_Cc)/gemOffset*latOffset
    Step4_Ct =  (Step3_Bg*Step2_Ac-Step2_Bc*Step3_Ag)/gemOffset*latOffset
    
    output += "STEP 4\n[4.4] At: {Step4_At}\n[4.4] Bt: {Step4_Bt}\n[4.4] Ct: {Step4_Ct}\n\n"

#STEP 5        
#Calculate coordinates of OTA
#De Hilster
#Coordinates centre OTA (with LAT-offset)
    Step5_Xrd = distD*np.cos(np.deg2rad(latitude))
    Step5_Yrd = 0
    Step5_Zrd = distD*np.sin(np.deg2rad(latitude))
    Step5_Xt = (dctbmX+bmtlaX+Step5_Xrd+Step3_Ag+Step4_At)
    Step5_Yt = (dctbmY+bmtlaY+Step5_Yrd+Step3_Bg+Step4_Bt)
    Step5_Zt = (dctbmZ+bmtlaZ+Step5_Zrd+Step3_Cg+Step4_Ct)

    output += f"STEP 5\n[5.1] Xrd: {Step5_Xrd}\n[5.2] Yrd: {Step5_Yrd}\n[5.3] Zrd: {Step5_Zrd}\n"
    output += f"[5.4] Xt: {Step5_Xt}\n[5.4] Yt: {Step5_Yt}\n[5.4] Zt: {Step5_Zt}\n\n"

#STEP 6        
#Step 1 in calculating intersection with sphere        
#Bourke
#Intersections are on m*u*u+n*u+o        
    Step6_m = sumsq([Step2_Bc,Step2_Ac,Step2_Cc])
    Step6_n = 2*(Step2_Ac*Step5_Xt+Step2_Bc*Step5_Yt+Step2_Cc*Step5_Zt)
    Step6_o = sumsq([Step5_Xt,Step5_Yt,Step5_Zt])-np.square(domeRadius)

    output += f"STEP 6\n[6.6] m: {Step6_m}\n[6.7] n: {Step6_n}\n[6.8] o: {Step6_o}\n\n"
    
#STEP 7    
#Check if step 6 holds a solution!    
#Bourke    
#How many intesections are there?    
#n*n-4m*o: <0: no int., =0: 1 int, >0: 2 int    
    Step7_discriminant = np.square(Step6_n)-4*Step6_m*Step6_o

    output += f"STEP 7\n[7.1] discriminant: {Step7_discriminant}\n\n"
    if (Step7_discriminant<0):
        output += "No intersections\n"
    if (Step7_discriminant==0):
        output += "One intersection\n"
    if (Step7_discriminant>0):
        output += "Two intersections\n"
    
#STEP 8    
#Solve u from step 6    
#Bourke    
#Two solutions for u    
    Step8_minusU = (-Step6_n-np.sqrt(Step7_discriminant))/(2*Step6_m)
    Step8_plusU = (-Step6_n+np.sqrt(Step7_discriminant))/(2*Step6_m)

#    output = "STEP 8\nStep8_minusU: "+Step8_minusU+"\nStep8_plusU: "+Step8_plusU+"\n\n"
    output += f"STEP 8\n[8] u: {Step8_plusU}\n\n"
    
#STEP 9                    
#Calculate intersection coordinates for both solutions                    
#Bourke                    
    Step9_minusXi = Step5_Xt+Step8_minusU*Step2_Ac
    Step9_minusYi = Step5_Yt+Step8_minusU*Step2_Bc
    Step9_minusZi = Step5_Zt+Step8_minusU*Step2_Cc
    Step9_plusXi = Step5_Xt+Step8_plusU*Step2_Ac
    Step9_plusYi = Step5_Yt+Step8_plusU*Step2_Bc
    Step9_plusZi = Step5_Zt+Step8_plusU*Step2_Cc

#    output = "Step9_minusXi: "+Step9_minusXi+"\nStep9_minusYi: "+Step9_minusYi+"\nStep9_minusZi: "+Step9_minusZi+"\n\n"
#    output += "Step9_plusXi: "+Step9_plusXi+"\nStep9_plusYi: "+Step9_plusYi+"\nStep9_plusZi: "+Step9_plusZi+"\n\n"
    output += f"STEP 9\n[9.1] Xi: {Step9_plusXi}\n[9.2] Yi: {Step9_plusYi}\n[9.3] Zi: {Step9_plusZi}\n\n"

#STEP 10    
#The required azimuth and Horizontal distance
#De Hilster    
#Dome azimuths
    if Step9_minusYi>0 and Step9_minusXi>0:
        val_Step9_test1 = 1
    else:
        val_Step9_test1 = 0

    Step10_minusAzi = np.rad2deg(np.arctan(Step9_minusYi/-Step9_minusXi))+180*(Step9_minusXi<0)+360*(val_Step9_test1)

    if Step9_plusYi>0 and Step9_plusXi>0:
        val_Step9_test2 = 1
    else:
        val_Step9_test2 = 0
    
    Step10_plusAzi  = np.rad2deg(np.arctan(Step9_plusYi/-Step9_plusXi))+180*(Step9_plusXi<0)+360*(val_Step9_test2)
    Step10_horDist = np.sqrt(sumsq([Step9_plusXi,Step9_plusYi]))

#    output += "STEP10\nStep10_minusAzi: "+Step10_minusAzi+"\nStep10_plusAzi: "+Step10_plusAzi+"\n\n"
    output += f"STEP10\n[10.2] Dome Azimuth: {Step10_plusAzi} degrees\n[10.3] Horizontal Distance: {Step10_horDist}\n\n"

    if display_report:
        print(output)

    dome_azimuth = Step10_plusAzi

    return dome_azimuth

def main():
    azimuth_dome = calc_azimuth(targetAzi=45,targetAlt=10,tube_side="east",display_report=True)
    print(f" azimuth Dome = {azimuth_dome:.01f} degree")

if __name__ == "__main__":
    main()	