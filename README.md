# README
As I upgraded my Prusa MK3S+ with a Raspberry Pi Zero 2W to print remotely without having it connected via USB to my main Pi running OctoPrint, I am missing the PrusaLevelingGuide-Plugin.

Probably works on the MK4 as well? Please test and report your experience through an issue.

While the printer does auto calibrate before each print I got more issues over time when printing as the printer had to many corrections on the fly while printing. To reduce this I recalibrated my plate with the plugin and octoprint until I consistently got less than .2mm deviation above the whole plate. To achieve this without having to use the OctoPrint-Plugin you can install this python script on your connected Pi Zero and run it via SSH to get the results in the Terminal.

You can set a preheating temperature via `--preheat <filament>` and adjust these settings in the filament.txt

You can change the serial port in line 7 of `calibrate.py`. Default should work though when using a Pi Zero. If you want to use this via USB from another Pi, adjust accordingly.

## Installation
1. Have SSH access
2. Update System\
`sudo apt update && sudo apt upgrade`
3. Install necessary python library if you don't want to set up a venv\
`sudo apt install python3-serial`

4. Get script
`wget https://github.com/pzauner/prusalevelingguide-cli-in-python-for-prusalink.git`

## Configuration
### Filaments
Set your own temperatures for the filaments in `filaments.txt`

## Usage

### Stop PrusaLink
`prusalink stop`

Use `prusalink start` after doing your adjustments to start it again.

### Without preheating
`python calibrate.py`
### With preheating
`python calibrate.py --preheat <filament>`

e.g.:\
`python calibrate.py --preheat PLA`


These are the default values:
```json
{
    "PLA": {"bed temp": 60, "nozzle temp": 215},
    "PETG": {"bed temp": 85, "nozzle temp": 235},
    "ABS": {"bed temp": 100, "nozzle temp": 240},
    "ASA": {"bed temp": 95, "nozzle temp": 240},
    "HIPS": {"bed temp": 95, "nozzle temp": 235},
    "SBS": {"bed temp": 70, "nozzle temp": 225},
    "Nylon": {"bed temp": 80, "nozzle temp": 250},
    "TPU": {"bed temp": 60, "nozzle temp": 225},
    "PVA": {"bed temp": 70, "nozzle temp": 225},
}
```

### Sample output

Number of measurements depends on your config. This
```
Num X,Y: 7,7
Measured points:
Raw 7x7 Grid Values:
0.138   0.164   0.160   0.155   0.158   0.132   0.147
0.161   0.212   0.215   0.163   0.179   0.168   0.145
0.154   0.214   0.207   0.172   0.164   0.165   0.114
0.127   0.196   0.177   0.156   0.159   0.145   0.115
0.147   0.219   0.215   0.178   0.169   0.182   0.136
0.157   0.207   0.202   0.172   0.165   0.167   0.133
0.146   0.168   0.193   0.141   0.169   0.140   0.127

3x3 Screw Adjustments:
Raw values:
-0.018  -0.001  -0.009
-0.029  0.00    -0.041
-0.01   -0.015  -0.029

Degrees:
13°CCW  1°CCW   6°CCW
21°CCW  0       30°CCW
7°CCW   11°CCW  21°CCW
```


## Related to
### Prusa Leveling Guide
See this OctoPrint-Plugin: [OctoPrint-PrusaLevelingGuide](https://github.com/scottrini/OctoPrint-PrusaLevelingGuide)
### G81 Relative
Straight up used the code of [g81_relative from pcboy](https://github.com/pcboy/g81_relative/blob/master/g81_relative.rb)

Asked Ghibidi to implement this into the current python script. Works. (After kicking it in the ass for a few times and comparing the results of my terminal output with the one from the [Website](https://pcboy.github.io/g81_relative/))

Original implementation rounds to two decimal places, while this script rounds to three decimal places.