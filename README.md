# python3-udp
UDP broadcast listener and parser

The UDP listener will capture broadcast packets containing weather data sent by ATMOCOM and log each record in a monthly SQLite database.

For convenience, a standalone executable for Windows that does not require Python3 pre-installed is also provided as well as a standalone binary for Raspberry Pi.

## Running atmoudp36.py and atmoudp36.exe
## Running atmoudp36.py script
Make sure a Python3 environment is installed and activated. Open a console window/command prompt and run the script:

python3 atmoudp36.py -p _passkey_

## Installing and running atmoudp36.bin standalone executable for Raspberry PI
Open a terminal window, create a dedicated directory for ATMOCOM script and data and enter it:
**pi@raspberrypi:** mkdir atmocom
**pi@raspberrypi:** cd atmocom

Download the atmoudp36.bin standalone binary file:
**pi@raspberrypi:** wget https://github.com/atmocom/python3-udp/raw/master/atmoudp36.bin

Change permissions of downloaded binary to make it executable:
**pi@raspberrypi:** chmod +x atmoudp36.bin

Run:
**pi@raspberrypi:** ./atmoudp36.bin -p _passkey_

## Installing and running atmoudp36.exe standalone executable for Windows
Download the executable and place it in a dedicated work folder on your Windows PC where you want your weather data to be logged. Open a Windows command prompt in this folder and type:

atmoudp36.exe -p _passkey_ **[ENTER]**

## All platforms
Replace _passkey_ with your own unique passkey that you configured in ATMOCOM. Also **do not forget** to enable UDP broadcast in ATMOCOM configuration settings! If prompted by Windows security, the program must be allowed through the firewall.

Once the program has started, if everything works correctly you will see weather data being printed on screen in the command window/terminal and logged in SQLite3 archives in a subfolder named **/wxdb**.

If you see ACCESS ERROR printed out after the string with captured UDP data that means that your script and ATMOCOM passkeys do not match.

To stop the program press and hold **CTRL+C** until the program terminates.

## Additional notes
By default the ATMOCOM UDP listener will store all captured weather data in metric units. To change this, add -i switch when starting the program, e.g. on Raspberry Pi you would have to start the standalone program like this:

**pi@raspberrypi:** ./atmoudp36.bin -i -p _passkey_
