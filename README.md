# Project2

This project uses Python to create a server and client that communicate with each other. The client requests data from a Raspberry Pi using vcgencmd commands and samples them 50 times. The data is displayed on the server and PySimpleGUI is used to display the client and server status, data that is being called and number of iterations the program has gone through. Threading is used to display data in the GUI while requesting and sending the data from client to server.

### Version 1
This version is just getting the client to server communication running and printing the result to the terminal.

### WIP
This folder contains all the iteratoins of code that it took to get the client and server programs to work as expected.

### Client
This folder contains the working client with the GUI that is functioning properly. The code could use some refactoring at a later date.

### Server
This folder contains the working server with the GUI. Again this code could use refactoring but it is working poroperly, so that can be done at another date.
