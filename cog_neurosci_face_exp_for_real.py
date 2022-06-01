# -*- coding: utf-8 -*-
""" DESCRIPTION:
This 2x2 fMRI experiment displays 2 different emoji faces (neutrual and fearful) in yellow and blue. Participants have to judge color with buttonpresses 'y' and 'b'.
The experiment lasts 8 minutes and has 100 trials.
The script awaits a trigger pulse from the scanner with the value "t"

/Mikkel Wallentin 2016 (with most of the code adapted from Jonas LindeLoev: https://github.com/lindeloev/psychopy-course/blob/master/ppc_template.py)

Structure: 
    SET VARIABLES
    GET PARTICIPANT INFO USING GUI
    SPECIFY TIMING AND MONITOR
    STIMULI
    OUTPUT
    FUNCTIONS FOR EXPERIMENTAL LOOP
    DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
    CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP

"""

# Import the modules that we need in this script
from __future__ import division
from psychopy import core, visual, event, gui, monitors, event
import pyglet
import time
import ppc
import glob

"""
SET VARIABLES
"""
# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor 
MON_WIDTH = 34  # Width of your monitor in cm
MON_SIZE = [1440, 900]  # Pixel-dimensions of your monitor
FRAME_RATE=60 # Hz
SAVE_FOLDER = 'face_exp_data'  # Log is saved to this folder. The folder is created if it does not exist.



"""
GET PARTICIPANT INFO USING GUI
"""
# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V= {'ID':'','age':'','gender':['male','female']}
if not gui.DlgFromDict(V, order=['ID', 'age', 'gender']).OK: # dialog box; order is a list of keys 
    core.quit()

"""
SPECIFY TIMING AND MONITOR
"""

# Clock and timer
clock = core.Clock()  # A clock wich will be used throughout the experiment to time events on a trial-per-trial basis (stimuli and reaction times).

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='deg', fullscr=[1280, 800], allowGUI=False, color='white')  # Initiate psychopy Window as the object "win", using the myMon object from last line. Use degree as units!

#Prepare Fixation cross
stim_fix = visual.TextStim(win, '+', color = 'black')#, height=FIX_HEIGHT)  # Fixation cross is just the character "+". Units are inherited from Window when not explicitly specified.
"""
STIMULI

"""
#EXPERIMANTAL DETAILS
# 12 min. exp.=720 sec. ->100 trials with stimulus duration 700 ms onset asyncrony of 4.8 s (i.e. 4.1 s fixation cross in between on average.

# a list of all image files (all .png files in the folder "img")
faces = glob.glob("faces/*.jpg")
faces_i = glob.glob("faces_i/*.jpg")
objects = glob.glob("objects/*.jpg")
objects_i = glob.glob("objects_i/*.jpg")

stimuli =  faces + faces_i + objects + objects_i

delays=(90,100,110,120) #different time intervals between stimuli mean 1,75 sec x 60 hz refresh rate =105, in order to make less predictable and increase power.
REPETITIONS = 1 # 100 different images * 3,6 sec time delay * 3 repetitions =  trials
dur=int(0.05*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
condition='face_exp' #Just a variable. If the script can run several exp. then this can be called in GUI. Not relevant here.

# The image size and position using ImageStim, file info added in trial list sbelow.
stim_image = visual.ImageStim(win,  # you don't have to use new lines for each attribute, but sometime it's easier to read that way
    mask=None,
    pos=(0.0, 0.0),
    size= (11.0, 13.8),
    ori=1)

""" OUTPUT """

#KEYS
#other important keys
KEYS_QUIT = ['escape']  # Keys that quits the experiment
KEYS_trigger=['t'] # The MR scanner sends a "t" to notify that it is starting
   # Prepare a csv log-file using the ppc script
writer = ppc.csvWriter(str(V['ID']), saveFolder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency

""" FUNCTIONS FOR EXPERIMENTAL LOOP"""

def make_trial_list(condition):
# Factorial design
    trial_list = []
    for stimulus in stimuli: # images
        for delay in delays:
                for rep in range(REPETITIONS):
                    # Add a dictionary for every trial
                    trial_list += [{
                        'ID': V['ID'],
                        'age': V['age'],
                        'gender': V['gender'],
                        'img': stimulus, #image file
                        'onset':'' ,# a place to note onsets
                        'offset': '',
                        'condition': condition,
                        'duration_measured':'',
                        'duration_frames': dur,
                        'delay_frames': delay,
                        'response': '',
                        'key_t':'',
                        'rt': '',
                        'correct_resp': ''
                    }]

# Randomize order
    from random import sample
    trial_list = sample(trial_list, len(trial_list))

    # Add trial numbers and return
    for i, trial in enumerate(trial_list):
        trial['no'] = i + 1  # start at 1 instead of 0
        if i is 0:
            writer.writeheader(trial) # An added line to give headers to the log-file (see ppc.py)
    return trial_list


def run_condition(condition):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    # Loop over trials
    for trial in make_trial_list(condition):
        event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        # Prepare image
        stim_image.image = trial['img']
        # Display image and monitor time
        time_flip=core.monotonicClock.getTime() #onset of stimulus
        for frame in range(trial['duration_frames']):
            stim_image.draw()
            win.flip()
        # Display fixation cross
        offset = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames']):
            stim_fix.draw()
            win.flip()
            # Get actual duration at offset
        #Log values
        trial['onset']=time_flip-exp_start
        trial['offset'] = offset-exp_start
        trial['duration_measured']=offset-time_flip
        try:
            key, time_key = event.getKeys(keyList=('y','b','escape'), timeStamped=True)[0]# timestamped according to core.monotonicClock.getTime() at keypress. Select the first and only answer.
        except IndexError:  #if no responses were given, the getKeys function produces an IndexError
            trial['response']=''
            trial['key_t']=''
            trial['rt']=''
            trial['correct_resp']=''
        else: #if responses were given, find RT and correct responses
            trial['response'] = key
            trial['key_t']= time_key-exp_start
            trial['rt'] = time_key-time_flip  #check if responses are correct
            if trial['response'] == 'y': #face
                trial['correct_resp'] = 1 if trial['img'] in faces or trial['img'] in faces_i else 0
            elif trial['response'] == 'b': #object
                trial['correct_resp'] = 1 if trial['img'] in objects or trial['img'] in objects_i else 0
            elif key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
                core.quit()
    writer.write(trial)        # Save trials to csv file

"""
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
"""    
textPos= [0, 0]                            # Position of question message
textHeight=0.75 # height in degrees
introText1=[u'Hey Kristian                    ',
                    u'',
                    u'Welcome to our experiment, we really appreciate your participation!',
                    u'',
                    u'In this experiment you have to look at faces and objects',
                    u'',
                    u'Press button with INDEX finger if the stimuli is an object',
                    u'',
                    u'Press button with MIDDLE finger if the stimuli is a face'] 


# Loop over lines in Intro Text1
ypos=4
xpos=0
for intro in introText1:
    ypos=ypos-1
    introText1 = visual.TextStim(win=win, text=intro, pos=[-6,ypos], height=textHeight, alignHoriz='left', color = 'black')
    introText1.draw()
win.flip()    # Show the stimuli on next monitor update and ...

#Wait for scanner trigger "t" to continue
event.waitKeys(keyList=KEYS_trigger)
exp_start=core.monotonicClock.getTime()


""" CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP"""

run_condition('face_exp')

