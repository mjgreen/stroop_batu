#!/opt/psychopy/PsychoPy-2025.1.1-Python3.10/.venv/bin/python

from psychopy import visual, data, core, gui
from psychopy.iohub import launchHubServer
from psychopy.core import getTime
from random import shuffle, choices
from psychopy.data import TrialHandler, importConditions
import string
from time import gmtime, strftime

date_and_time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
random_string = ''.join(choices(string.ascii_uppercase + string.digits, k=10))

myDlg = gui.Dlg(title="Batu Stroop v1")
myDlg.addField('ID_NUMBER:', 0)
myDlg.addField('ID_DATE:', strftime("%Y-%m-%d_%H:%M:%S", gmtime()))
myDlg.addField('ID_RANDOM:', random_string)
myDlg.addField('Block:', choices=['A', 'B', 'C', 'D', 'E'])
myDlg.addField('Type of session:', choices=["Real Run", "Practice"])
myDlg.addField('Trial duration:', choices=[5.0, 2.0])
dialog = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # or if ok_data is not None
    print(dialog)
else:
    print('user cancelled')
    core.quit()

this_block = "BLOCK"+dialog['Block:']+".xlsx"
trial_duration = float(dialog['Trial duration:'])
print(trial_duration)

win = visual.Window([800, 600], fullscr=False, units='height', monitor='fmri')
io = launchHubServer(
    window=win,
    experiment_code="batustroop",
    session_code=dialog['ID_RANDOM:'])

# Initiate components
button_box = io.devices.keyboard
word = visual.TextStim(win, text="dummy-word", color="white", pos=(0,0))
dev_feedback = visual.TextStim(win, text="dummy-dev_feedback", color="black", pos=(0,-.25))

# Read spreadsheet trial definitions
session = this_block
trial_definitions = importConditions(session)
trials = TrialHandler(trialList=trial_definitions, nReps=1, method = 'random')
# Inform the ioHub server about the TrialHandler
io.createTrialHandlerRecordTable(trials)

# Set non-csv vars
iti_base = 0.25
all_jitters = [0.25,0.275,0.3,0.325,0.35,.375,0.4,0.425,0.45,0.475,0.5,0.525,0.5,0.575,0.6,0.625,0.65,0.675,0.7,0.725,0.75]
ntrials=0
for trial in trials:
    ntrials+=1
    print(f'Trial {ntrials} Starting')
    word.setText(trial['word'])
    word.setColor(trial['colour'])
    word.draw()
    win.flip()
    t0 = getTime()
    button_box.reporting = True
    while getTime()-t0 <= trial_duration:
        events = button_box.getEvents()
        for event in events:
            if event.type == button_box.KEY_PRESS:
                print(f'\tPress: {event.key} at {round(event.time - t0,3)}')
                dev_feedback.setText(event.key)
                dev_feedback.draw()
                word.draw()
                win.flip()
                trial_response = event.key
                if event.key == 'q' or event.key == 'escape':
                    io.quit()
                    core.quit()
            if event.type == button_box.KEY_RELEASE:
                print(f'\tRelease: {event.key} at {round(event.time - t0,3)}')
        if events:
            button_box.reporting = False
    win.flip()
    shuffle(all_jitters)
    iti = iti_base + all_jitters[1]
    core.wait(iti)
    trial['this_iti'] = iti
    trial['this_block'] = this_block
    trial['key'] = trial_response
    # At the end of each trial, before getting the next trial handler row, send the trial variable states to iohub so they can be stored for future reference.
    io.addTrialHandlerRecord(trial)
    

io.quit()