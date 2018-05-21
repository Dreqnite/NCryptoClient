# NCryptoClient
A client-side application of the NCryptoChat. This project is created with a purpose of studying Python, so it is not recommended to use NCryptoClient in real projects.

## How to install and use NCryptoClient
*Note: Installation of NCryptoServer is needed, otherwise NCryptoClient will not work!*  
**Using PyPi:**
* Install distributions which are stored in PyPi: `pip install NCryptoClient`. NCryptoTools, which is required to run the NCryptoClient, will be installed automatically.
* If installation is successfull, it will be possible to run application in a two modes:  
  * Console mode (all errors and warnings will be showed): `NCryptoClient_console`.
  * GUI mode (all errors and warnings will be hidden): `NCryptoClient_gui`.  

**Using this repository:**
* Install NCryptoTools from PyPi: `pip install NCryptoTools`.
* Clone this repository to your local computer.
* From the root directory of the NCryptoClient project execute in the console: `python -m NCryptoClient.launcher`.