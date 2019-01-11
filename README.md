# python3-udp
UDP broadcast listener and parser

The UDP listener will capture broadcast packets containing weather data sent by ATMOCOM and log each record in a monthly SQLite database.

For convenience, a standalone executable for Windows that does not require Python3 pre-installed is also provided.

## Running atmoudp36.py and atmoudp36.exe
### Running atmoudp36.py script
Make sure a Python3 environment is installed and activated. Open a console window/command prompt and run the script:

python atmoudp36.py -p _passkey_

### Running atmoudp36.exe standalone executable
Download the executable and place it in a dedicated work folder on your Windows PC where you want your weather data to be logged. Open a Windows command prompt in this folder and type:

atmoudp36.exe -p _passkey_ **[ENTER]**

### All platforms
Replace _passkey_ with your own unique passkey that you configured in ATMOCOM. Also **do not forget** to enable UDP broadcast in ATMOCOM configuration settings! If prompted by Windows security, the program must be allowed through the firewall.

Once the program has started, if everything works as it should you will see weather data being logged and stored in SQLite3 archives in a subfolder named **/wxdb**.

To stop the program press and hold **CTRL+C** until the program terminates.
