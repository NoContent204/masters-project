Final Year Project for degree of MSci Computer Science - University of Birmingham
Alexander Nutt - 2165043

Set up:
SocketCAN is built into the kernel of most modern Linux system but it is also recommeneded that you install the can-utils package
`sudo apt-get install can-utils`

You can install the dependecies for this project with
`pip install -r requirements.txt`


This project implements a black-box fuzzer for the automotive Unified Diagnostic Services (UDS) protocol.

The main program of this project is uds-fuzzer.py
You can get help for running the program with the `-h` option
`python3 uds-fuzzer.py -h`

There other options are as follows:
`-g`: Enable use of the BNF grammar for input generation 
`-m`: Enable use of mutations on inputs
`-mi`: Use in conjunction with `-m` to set the number of iterations of muatations
`-r`: Enable the use of radmasa for mutation of inputs

`-d`: Enable the use of DTCs for ECU feedback
`-ti`: Enable the use of response timing for ECU feedback
`-tr`: Enable the use of traffic monitoring for ECU feedback

The program will stored the inputs it has used, the inputs it found to be potenially useful, a recording of the initial traffic, the recording of new traffic and the sorted traffic in `./results/yyy-mm-dd_hh:mm:ss` 




