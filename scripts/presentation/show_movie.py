#!/usr/bin/env python
import sys
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, gui, event, logging
from psychopy import sound, core
import time as ptime
import serial
import os
import fcntl
from os.path import join as pjoin, exists as pexists
import json
import csv
import datetime
import shutil

import input_utils as inut

skip_response = False
debug = False

# add a new level name called bids
# we will use this level to log information that will be saved
# in the _events.tsv file for this run
BIDS = 26
logging.addLevel(BIDS, 'BIDS')
STOP_TRIGGER = 'p'


def logbids(msg, t=None, obj=None):
    """logbids(message)
    logs a BIDS related message
    """
    logging.root.log(msg, level=BIDS, t=t, obj=obj)


logging.console.setLevel(logging.INFO)  # receive nearly all messages
time_template = '%Y%m%dT%H%M%S'


def write_subjectlog(fn, info):
    fieldnames = ['subject_id', 'run_nr', 'timestamp']
    info_save = {key: info.get(key, '') for key in fieldnames}
    with open(fn, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        info_save['timestamp'] = datetime.datetime.now().isoformat()
        writer.writerow(info_save)


def load_subjectlog(fn):
    lastinfo = {
        'subject_id': 'sidXXXXXX',
        'run_nr': 1
    }
    if not pexists(fn):
        with open(fn, 'w') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['subject_id',
                                                'run_nr',
                                                'timestamp'],
                                    delimiter='\t')
            writer.writeheader()
    else:
        with open(fn, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = [r for r in reader]
            lastinfo = rows[-1]
    return lastinfo


# load config
with open('config.json', 'r') as f:
    config = json.load(f)

instructions = config['instructions']
n_parts = len(config['files'])
fixation_s = config['fixation_s']
subjectlog = config['log_subjects']
lastinfo = load_subjectlog(subjectlog)

# ask info to experimenter
info = {
    'subject_id': lastinfo['subject_id'],
    'run_nr': 2,
    'scanner?': True,
}
infdlg = gui.DlgFromDict(dictionary=info,
                         title="Movie Presentation",
                         order=['subject_id', 'run_nr', 'scanner?']
                         )
if not infdlg.OK:
    core.quit()
# save log of subjects
write_subjectlog(subjectlog, info)

part = int(info['run_nr'])
subj = info['subject_id']

with open('subjectvolume.json', 'r') as f:
    try:
        MOVIE_VOLUME = json.load(f)[subj]
    except KeyError:
        logging.warn("Subject {0} not present in volume file, "
                     "using default volume as 0.8")
        MOVIE_VOLUME = 0.8

time = core.Clock()
STIMDIR = "stim"
RESDIR = "res"
RESDIR = pjoin(RESDIR, subj)
if not pexists(RESDIR):
    os.makedirs(RESDIR)

log_fn = config['log_template'].format(
    subj=subj,
    task_name=config['task_name'],
    runnr=part,
    timestamp=ptime.strftime(time_template),
)
log_fn = pjoin(RESDIR, log_fn)
log_responses = logging.LogFile(log_fn, level=logging.INFO)


def move_halted_log(fn):
    # flush log
    logging.flush()
    shutil.move(fn, fn.replace('.txt', '__halted.txt'))
    # quit
    core.quit()

# set up global key for quitting; if that happens, log will be moved to
# {log_fn}__halted.txt
event.globalKeys.add(key='q',
                     modifiers=['ctrl'],
                     func=move_halted_log,
                     func_args=[log_fn],
                     name='quit experiment gracefully')

# @aim: added parentheses for print statement
print("Opening screen")
tbegin = time.getTime()
using_scanner = info['scanner?']
# Setting up visual
if using_scanner:
    size = [1024, 768]
    fullscr = True
else:
    size = [1024, 768]
    fullscr = False
scrwin = visual.Window(size=size,
                       allowGUI=False, units='pix',
                       screen=0, rgb=[-1, -1, -1],
                       fullscr=fullscr)
# loading movie clip
# @aim: added parentheses for print statement
print("Loading movie part")
clip = config['files'][part - 1]
clip = pjoin(STIMDIR, clip)
loading = visual.TextStim(scrwin,
                          text=instructions,
                          height=31)
loading.draw()
scrwin.flip()
# @aim: MovieStim3 --> MovieStim
movie = visual.MovieStim(scrwin, clip,
                          # this looks nice if file is in 16:9
                          # and frame size is 720 x 406
                          size=(1024, 577),
                          name='movie_part_{0}'.format(part))
# @aim: _audioStream.setVolume() --> set volume property
movie.volume = MOVIE_VOLUME
scrwin.flip()
cross_hair = visual.TextStim(scrwin, text='+', height=31,
                             pos=(0, 0), color='#FFFFFF')


if using_scanner:
    intro_msg = "Waiting for trigger..."
else:
    intro_msg = "Press Enter to start"
intro = visual.TextStim(scrwin, text=intro_msg, height=31)

# Start of experiment
intro.draw()
scrwin.flip()

# @aim: open up serial port and wait for first trigger
trigger_file = os.open('/dev/hidraw1', os.O_RDONLY)
flags = fcntl.fcntl(trigger_file, fcntl.F_GETFL)
fcntl.fcntl(trigger_file, fcntl.F_SETFL, flags | os.O_NONBLOCK)

if using_scanner:
    # @aim: new trigger for MIT scanner
    inut.check_trigger_fd(trigger_file)
    print('passed')
else:
    # @aim: import launchScan from psychopy_mri_emulator instead of psychopy.hardware.emulator
    from psychopy_mri_emulator import launchScan
    event.waitKeys(keyList=['return'])
    # XXX: set up TR here
    MR_settings = {
        'TR': 1,
        'volumes': 280,
        'sync': '5',
        'skip': 3,
        'sound': False,
    }
    vol = launchScan(scrwin, MR_settings, globalClock=time, mode='Test')

    class FakeSerial(object):
        @staticmethod
        def read():
            k = event.getKeys(['1', '2', '5'])
            return k[-1] if k else ''
    ser = FakeSerial()

# set up timer for experiment starting from first trigger
logging.exp("EXPERIMENT STARTING")
timer_exp = core.Clock()
trunbegin = timer_exp.getTime()
lasttrigger = trunbegin
cross_hair.draw()
scrwin.flip()
# setup bids log
logbids("onset\tduration\tframeidx\tvideotime\tlasttrigger")
# duration will be filled later
template_bids = '{onset:.3f}\t{{duration:.3f}}\t{frameidx}\t{videotime:.3f}' \
                '\t{lasttrigger:.3f}'

# wait for fixation
while timer_exp.getTime() - trunbegin < fixation_s: 
    continue

iflips = 1
logging.exp("MOVIE STARTING")
logging.flush()
while not movie.isFinished:
    movie.draw()
    scrwin.flip()
    # save times
    onset = timer_exp.getTime()
    # @aim: getCurrentFrameTime() --> .pts property
    videotime = movie.pts
    logbids(template_bids.format(
        onset=onset,
        frameidx=iflips,
        videotime=videotime,
        lasttrigger=lasttrigger
    ))
    # log every 30 second
    if iflips % 1800 == 0:
        logging.exp("MOVIE: FLIP {0:06d} ({1:.02f}s since start)".format(
            iflips, time.getTime() - trunbegin))
        logging.flush()
    iflips += 1

#     # @aim: removed the trigger info
#     if inut.check_trigger_fd(trigger_file):
#         logging.info("TRIGGER")
#         lasttrigger = timer_exp.getTime()
# 
# 
#     elif ser.read() == STOP_TRIGGER:
#         movie.stop()
#         break

os.close(trigger_file)

logging.exp("MOVIE FINISHED")
scrwin.flip()
# wait 10 seconds at the end
cross_hair.draw()
core.wait(fixation_s)
tend = time.getTime()
logging.exp("EXPERIMENT FINISHED")
logging.exp("Done in {0:.2f}s".format(tend-tbegin))
logging.flush()
scrwin.close()
core.quit()
