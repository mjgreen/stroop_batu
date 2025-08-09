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
myDlg.addField('Block:', choices=['Z','A', 'B', 'C', 'D', 'E'])
myDlg.addField('Type of session:', choices=["Real Run", "Practice"])
myDlg.addField('Trial duration:', choices=[2, 5])
dialog = myDlg.show()  
if myDlg.OK:  
    print(dialog)
else:
    print('user cancelled')
    core.quit()

this_block = "BLOCK"+dialog['Block:']+".csv"
trial_duration = float(dialog['Trial duration:'])
print(trial_duration)
session_code = str(dialog['ID_NUMBER:']) + "_" + str(dialog['ID_RANDOM:'])
print(session_code)

win = visual.Window([800, 600], fullscr=True, units='height', monitor='fmri', screen=1)

io = launchHubServer(
    window = win,
    experiment_code = "data/batustroop",
    session_code = session_code
    )

# Initiate components
button_box = io.devices.keyboard
word = visual.TextStim(win, text="dummy-word", color="white", pos=(0,0))
dev_feedback = visual.TextStim(win, text="dummy-dev_feedback", color="black", pos=(0,-.25), height=0.05)
waiting = visual.TextStim(win, text="Waiting ...", color="black", pos=(0,-.25), height=0.05)

# Read spreadsheet trial definitions
trial_definitions = importConditions(this_block)
trials = TrialHandler(trialList=trial_definitions, nReps=1, method = 'random')
# Inform the ioHub server about the TrialHandler
io.createTrialHandlerRecordTable(trials)

# Set non-csv vars
iti_base = 0.25
all_jitters = [0.25,0.275,0.3,0.325,0.35,.375,0.4,0.425,0.45,0.475,0.5,0.525,0.5,0.575,0.6,0.625,0.65,0.675,0.7,0.725,0.75]
ntrials=0

# Wait for T from scanner
waiting.draw()
win.flip()
button_box.reporting = True
t_received = False
while not t_received:
    tpresses = button_box.getPresses(keys=['t'])
    if tpresses:
        button_box.reporting = False
        for tpress in tpresses:
            time_of_first_t = tpress.time

win.flip()

# Start trial loop
for trial in trials:
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
                dev_feedback.setText(press.key+" at "+str(round(press.time-stimulus_on,3)))
                dev_feedback.draw()
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
    trial['rt'] = press.time - stimulus_on
    trial['trial_number'] = ntrials
    trial['randomid'] = dialog['ID_RANDOM:']
    trial['subject_number'] = dialog['ID_NUMBER:']
    trial['session_time'] = dialog['ID_DATE:']
    trial['accuracy'] = int(trial['key'] == trial['correct_response'])
    trial['response'] = press.key
    trial['response_on'] = press.time
    trial['trial_number'] = ntrials
    trial['randomid'] = dialog['ID_RANDOM:']
    trial['subject_number'] = dialog['ID_NUMBER:']
    trial['session_time'] = dialog['ID_DATE:']
    trial['time_of_first_t'] = time_of_first_t
    trial['stimulus_on'] = stimulus_on
    trial['stimulus_off'] = stimulus_off
    trial['iti_on'] = iti_on
    trial['iti_off'] = iti_off
    trial['iti_dur'] = iti
    trial['trial_start_time'] = trial_start_time
    # At the end of each trial, before getting the next trial handler row, send the trial variable states to iohub so they can be stored for future reference.
    io.addTrialHandlerRecord(trial)
io.quit()

