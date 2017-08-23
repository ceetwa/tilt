# tilt
Scripts for interacting with Tilt Hydrometer

Copied from orignal instructions here: http://www.instructables.com/id/Reading-a-Tilt-Hydrometer-With-a-Raspberry-Pi/

Usage:
I run the script tilt_oneshot.py as a sudo cronjob like this
*/10 * * * * /path/to/tilt_oneshot.py purple "Beer Name,3" "https://script.google.com/macros/s/yourSheetID/exec"

which will log data every 10 mins
