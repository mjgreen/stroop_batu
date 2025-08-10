#!/opt/psychopy/PsychoPy-2025.1.1-Python3.10/.venv/bin/python

from psychopy import visual, data, core, gui
from psychopy.iohub import launchHubServer
from psychopy.core import getTime
from random import shuffle, choices
from psychopy.data import TrialHandler, importConditions
import string
from time import gmtime, strftime

# Set up the dialogue box for the experimenter
date_and_time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
random_string = ''.join(choices(string.ascii_uppercase + string.digits, k=10))
myDlg = gui.Dlg(title="Batu Stroop v1")
myDlg.addField('ID_NUMBER:', "0")
myDlg.addField('ID_DATE:', strftime("%Y-%m-%d_%H:%M:%S", gmtime()))
myDlg.addField('ID_RANDOM:', random_string)
myDlg.addField('Block:', choices=['Z','A', 'B', 'C', 'D', 'E'])
myDlg.addField('Trial duration:', choices=[2, 5])
dialog = myDlg.show()  
if myDlg.OK:  
    print(dialog)
else:
    print('user cancelled')
    core.quit()

# Choose spreadsheet based on dialog box response
this_block = "BLOCK"+dialog['Block:']+".csv"

# Print to terminal for the experimenter's benefit
trial_duration = float(dialog['Trial duration:'])
print("Trial duration was set to " + str(trial_duration))
session_code = str(dialog['ID_NUMBER:']) + "_" + str(dialog['ID_RANDOM:'])
print("Session code is " + str(session_code))

# Set up the window for the experiment to run in
win = visual.Window([800, 600], fullscr=True, units='height', monitor='fmri', screen=1)
# win = visual.Window([800, 600], fullscr=False, units='height', monitor='matt', screen=0)

# Start hdf5 file to capture results
io = launchHubServer(
    window = win,
    experiment_code = "batustroop",
    session_code = session_code
    )

# Initiate hardware components
button_box = io.devices.keyboard

# Initate stimulus components
waiting = visual.TextStim(win, text="Get Ready ...", color="black", pos=(0,-.25), height=0.05)
dev_feedback = visual.TextStim(win, text="dummy-dev_feedback", color="black", pos=(0,-.25), height=0.05)
word = visual.TextStim(win, text="dummy-word", color="white", pos=(0,0))

# Read spreadsheet trial definitions into psychopy
trial_definitions = importConditions(this_block)
trials = TrialHandler(trialList=trial_definitions, nReps=1, method = 'random')

# Inform the ioHub server about the TrialHandler
io.createTrialHandlerRecordTable(trials)

# Prepare variable ITIs
iti_base = 0.25
all_jitters = [0.25,0.275,0.3,0.325,0.35,.375,0.4,0.425,0.45,0.475,0.5,0.525,0.5,0.575,0.6,0.625,0.65,0.675,0.7,0.725,0.75]

# Wait for T from scanner
doWait = True
waiting.draw()
win.flip()
button_box.reporting = True
button_box.clearEvents()
while doWait:
    tpresses = button_box.getPresses(keys=['t'], clear=True)
    if tpresses:
        doWait = False
        button_box.reporting = False
        button_box.clearEvents()
        for tpress in tpresses:
            time_of_first_t = tpress.time
win.flip()

# Start trials loop
ntrials = 0
for trial in trials:
    trial['rt'] = None
    trial['accuracy'] = None
    trial['response'] = None
    trial['response_on'] = None
    trial_start_time = getTime()
    ntrials += 1
    print(f'Trial {ntrials} Starting')
    word.setText(trial['word'])
    word.setColor(trial['colour'])
    word.draw()
    stimulus_on = win.flip()
    button_box.reporting = True
    button_box.clearEvents()
    while getTime() - stimulus_on <= trial_duration:
        presses = button_box.getPresses(keys=['r','g','b','y','e','w','n','d','q'], clear=True)  
        if presses:
            button_box.reporting = False
            for press in presses:
                trial['rt'] = press.time - stimulus_on
                trial['accuracy'] = int(press.key == trial['correct_response'])
                trial['response'] = press.key
                trial['response_on'] = press.time
                # Uncomment to get experimnter-aimed feedback to see if the button-box is working
                # dev_feedback.setText(press.key+" at "+str(round(press.time-stimulus_on,3)))
                # dev_feedback.draw()
                word.draw()
                win.flip()
    stimulus_off = win.flip()
    shuffle(all_jitters)
    iti = iti_base + all_jitters[1]
    iti_on = getTime()
    core.wait(iti)
    iti_off = getTime()
    # explicitly add vars to the trial record
    trial['session_code'] = session_code
    trial['trial_number'] = ntrials
    trial['randomid'] = dialog['ID_RANDOM:']
    trial['subject_number'] = dialog['ID_NUMBER:']
    trial['session_time'] = dialog['ID_DATE:']
    trial['trial_start_time'] = trial_start_time
    trial['time_of_first_t'] = time_of_first_t
    trial['stimulus_on'] = stimulus_on
    trial['stimulus_off'] = stimulus_off
    trial['iti_on'] = iti_on
    trial['iti_off'] = iti_off
    trial['iti_dur'] = iti
    # At the end of each trial, before getting the next trial handler row, 
    # send the trial variable states to iohub so they can be stored for future reference.
    # Otherwise the data won't be stored
    io.addTrialHandlerRecord(trial)
io.quit()

