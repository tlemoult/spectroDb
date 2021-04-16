#if 0
Modified by Thierry Lemoult, to try a simple CCD acquisition

Simple Client Tutorial
Demonstration of libindi v0.7 capabilities.

Copyright (C) 2010 Jasem Mutlaq (mutlaqja@ikarustech.com)

This library is free software;
you can redistribute it and / or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation;
either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY;
without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library;
if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110 - 1301  USA

#endif

/** \file tutorial_client.cpp
    \brief Construct a basic INDI client that demonstrates INDI::Client capabilities. This client must be used with tutorial_three device "Simple CCD".
    \author Jasem Mutlaq

    \example tutorial_client.cpp
    Construct a basic INDI client that demonstrates INDI::Client capabilities. This client must be used with tutorial_three device "Simple CCD".
    To run the example, you must first run tutorial_three:
    \code indiserver tutorial_three \endcode
    Then in another terminal, run the client:
    \code tutorial_client \endcode
    The client will connect to the CCD driver and attempts to change the CCD temperature.
*/

#include "myClient.h"

#include "indibase/basedevice.h"

#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <unistd.h>

#define MYCCD "ZWO CCD ASI120MM"



int main(int argc, char *argv[])
{
       
    printf("Total number of command line arguments = %d \n",argc);
    if (argc!=8) { 
        printf("Invalid number of argument. The correct usage is:\n");
        printf("  ./myClient ipAdress port \"Camera Name\" binX binY expTime \"outputFilename.fits\" \n");
        printf("  ./myClient localhost 7624 \"ZWO CCD ASI120MM\" 1 1 1.5 \"./finder.fits\" \n");
        exit(0);
    }
    for(int i = 0; i < argc; i++) { printf("Argument index = %d , Argument = %s\n",i, argv[i]);  }

    char *serverAddress = argv[1];
    int serverPort = atoi(argv[2]);
    char *myCCD = argv[3];
    float expTime;
    int binX = atoi(argv[4]);
    int binY = atoi(argv[5]);
    sscanf(argv[6], "%f", &expTime);
    char *savePathFilename = argv[7];
    
    static std::unique_ptr<MyClient> camera_client(new MyClient(myCCD,savePathFilename));
    
    printf("Connecting to indiserver:  address = \"%s\"  port = %d\n",serverAddress,serverPort);
    camera_client->setServer("localhost", 7624);

    printf("myCCD is \"%s\" \n",myCCD);
    printf("binning is: BinX=%d BinY=%d\n",binX,binY);
    printf("expTime is %f seconds\n",expTime);
    printf("savePathFilename = \"%s\"\n",savePathFilename);

    camera_client->watchDevice(myCCD);

    camera_client->connectServer();

    camera_client->setBLOBMode(B_ALSO, myCCD, nullptr);
    
    do { usleep(1000*100); } while(!(camera_client->isConnected()));

    camera_client->setBinning(binX,binY);
//    camera_client->setTemperature(0);
    camera_client->takeExposure(expTime);

    do { usleep(1000*100); }  while(camera_client->status != Finished);
        
    std::cout << "End of acquisition process.\n";

}

/**************************************************************************************
**
***************************************************************************************/
MyClient::MyClient(char *CCDname,char *pathFileName)
{
    ccd_device = nullptr;
    status = Stop;
    myCCD = CCDname;
    savePathFileName = pathFileName;
}

/**************************************************************************************
**
***************************************************************************************/
int MyClient::isConnected()
{
    if (ccd_device != nullptr)
    {
        if (ccd_device->isConnected()) { return 1; } else { return 0;}
    }
    else
    {
        return 0;
    }
}


/**************************************************************************************
**
***************************************************************************************/
void MyClient::setTemperature(int tempSetting)
{
    INumberVectorProperty *ccd_temperature = nullptr;

    ccd_temperature = ccd_device->getNumber("CCD_TEMPERATURE");

    if (ccd_temperature == nullptr)
    {
        IDLog("Error: unable to find CCD_TEMPERATURE property.\n");
        return;
    }

    IDLog("setTemperature to %d celcius degree.\n",tempSetting);
    ccd_temperature->np[0].value = tempSetting;
    sendNewNumber(ccd_temperature);
}

void MyClient::setBinning(int binX,int binY)
{
    INumberVectorProperty  *ccd_binning = nullptr;
    ccd_binning = ccd_device->getNumber("CCD_BINNING");
    if (ccd_binning == nullptr)
    {
        IDLog("Error: unable to find CCD_BINNING property\n");
        return;
    }
    IDLog("setBinning (X,Y) to (%d,%d)\n",binX,binY);
    ccd_binning->np[0].value = binX;
    ccd_binning->np[1].value = binY;
    sendNewNumber(ccd_binning);

}

/**************************************************************************************
**
***************************************************************************************/
void MyClient::takeExposure(float duration)
{
    INumberVectorProperty *ccd_exposure = nullptr;

    ccd_exposure = ccd_device->getNumber("CCD_EXPOSURE");

    if (ccd_exposure == nullptr)
    {
        IDLog("Error: unable to find CCD_EXPOSURE property...\n");
        return;
    }

    // Take a 1 second exposure
    IDLog("Taking a %f second exposure.\n",duration);
    ccd_exposure->np[0].value = duration;
    sendNewNumber(ccd_exposure);
    status = Running;
}

/**************************************************************************************
**
***************************************************************************************/
void MyClient::newDevice(INDI::BaseDevice *dp)
{
    if (strcmp(dp->getDeviceName(), myCCD) == 0)
        IDLog("Receiving %s Device...\n", dp->getDeviceName());

    ccd_device = dp;
}

/**************************************************************************************
**
*************************************************************************************/
void MyClient::newProperty(INDI::Property *property)
{
    if (strcmp(property->getDeviceName(), myCCD) == 0)
    {
        if (strcmp(property->getName(), "CONNECTION") == 0)
        {
            connectDevice(MYCCD);
            return;
        }

        if (strcmp(property->getName(), "CCD_TEMPERATURE") == 0)
        {
            if (ccd_device->isConnected())
            {
                IDLog("CCD is connected.\n");
            }
            return;
        }
    }
}

/**************************************************************************************
**
***************************************************************************************/
void MyClient::newNumber(INumberVectorProperty *nvp)
{
    if (strcmp(nvp->device, myCCD) == 0)
    {
        // Let's check if we get any new values for CCD_TEMPERATURE
        if (strcmp(nvp->name, "CCD_TEMPERATURE") == 0)
        {
            IDLog("Receving new CCD Temperature: %g C\n", nvp->np[0].value);
        }

        if (strcmp(nvp->name, "CCD_EXPOSURE") == 0)
        {
            IDLog("Receving new CCD Exposure: %g \n", nvp->np[0].value);
        }
    }
}

/**************************************************************************************
**
***************************************************************************************/
void MyClient::newMessage(INDI::BaseDevice *dp, int messageID)
{
    if (strcmp(dp->getDeviceName(), myCCD) != 0)
        return;

    IDLog("Receving message from Server:\n\n########################\n%s\n########################\n\n",
          dp->messageQueue(messageID).c_str());
}

/**************************************************************************************
**
***************************************************************************************/
void MyClient::newBLOB(IBLOB *bp)
{
    // Save FITS file to disk
    std::ofstream myfile;
    
    if (strcmp(bp->bvp->device, myCCD) == 0)
    {

        myfile.open(savePathFileName, std::ios::out | std::ios::binary);

        myfile.write(static_cast<char *>(bp->blob), bp->bloblen);

        myfile.close();

        IDLog("Received image, from %s saved as %s\n",myCCD,savePathFileName);
        status = Finished;
    }
    else
    {
        IDLog("Received image from other device name = %s \n",bp->bvp->device);
    }
    
}
