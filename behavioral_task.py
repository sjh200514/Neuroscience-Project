from psychopy import visual, core, event, data, gui
import numpy as np
import random

N_CHOICES = 6
N_PRACTICE = 5
N_REPS_MAIN = 3
COHERENCE_LEVELS = [0.05, 0.1, 0.15]

TARGET_RADIUS = 250
DOT_SPEED = 1.5
DOT_LIFETIME = 40
DOT_SIZE = 6
TEXT_HEIGHT = 22

def get_layout_config(radius):
    sin60 = np.sin(np.deg2rad(60)) * radius
    cos60 = np.cos(np.deg2rad(60)) * radius

    return [
        {'ang': 0,   'pos': (radius, 0),   'keys': ['d', 'num_6', '6'], 'label': 'D / 6'},
        {'ang': 60,  'pos': (cos60, sin60),'keys': ['e', 'num_9', '9'], 'label': 'E / 9'},
        {'ang': 120, 'pos': (-cos60, sin60),'keys': ['q', 'w', 'num_7', '7'], 'label': 'Q / 7'},
        {'ang': 180, 'pos': (-radius, 0),  'keys': ['a', 'num_4', '4'], 'label': 'A / 4'},
        {'ang': 240, 'pos': (-cos60, -sin60),'keys': ['z', 'num_1', '1'], 'label': 'Z / 1'},
        {'ang': 300, 'pos': (cos60, -sin60),'keys': ['x', 'c', 'num_3', '3'], 'label': 'X / 3'}
    ]
exp_info = {'Participant': '001'}
dlg = gui.DlgFromDict(dictionary=exp_info, title='DDM Experiment')
if not dlg.OK: core.quit()

this_exp = data.ExperimentHandler(name='6Choice_DDM', version='Numpad_Added',
                                  extraInfo=exp_info, 
                                  dataFileName=f'data/{exp_info["Participant"]}_Exp')

win = visual.Window(size=[1200, 900], color='black', units='pix', fullscr=False)

layout_config = get_layout_config(TARGET_RADIUS)
allowed_keys = []
for item in layout_config:
    allowed_keys.extend(item['keys'])
allowed_keys.append('escape')

target_circles = []
target_labels = []

for item in layout_config:
    circ = visual.Circle(win, radius=35, edges=32, pos=item['pos'], 
                         lineColor='white', fillColor=None, lineWidth=2)
    target_circles.append(circ)
    txt = visual.TextStim(win, text=item['label'], pos=item['pos'], 
                          color='yellow', height=TEXT_HEIGHT, bold=True)
    target_labels.append(txt)

dots = visual.DotStim(win=win, nDots=250, fieldSize=(300, 300), dotSize=DOT_SIZE, speed=DOT_SPEED, 
                      dir=0.0, coherence=0.5, fieldShape='circle', color='white', 
                      signalDots='same', dotLife=DOT_LIFETIME)

correction_text = visual.TextStim(win, text="正确答案!", color='lime', height=TEXT_HEIGHT*0.9)
rt_text = visual.TextStim(win, text="", pos=(0, 0), height=32, bold=True)
progress_text = visual.TextStim(win, text="", pos=(0, 380), height=24, color='gray', alignText='center')

def run_single_trial(target_angle, coherence, correct_keys, target_pos, progress_str=""):
    dots.dir = target_angle
    dots.coherence = coherence
    progress_text.text = progress_str 
    
    for circ in target_circles:
        circ.lineColor = 'white'
        circ.lineWidth = 2

    # Fixation
    visual.TextStim(win, text='+', height=40).draw()
    for circ, lbl in zip(target_circles, target_labels):
        circ.draw()
        lbl.draw()
    progress_text.draw()
    win.flip()
    core.wait(0.5)

    # Stimulus
    event.clearEvents()
    rt_clock = core.Clock()
    keys = []
    
    while not keys:
        for circ, lbl in zip(target_circles, target_labels):
            circ.draw()
            lbl.draw()
        dots.draw()
        progress_text.draw()
        win.flip()
        
        keys = event.getKeys(keyList=allowed_keys)
        if 'escape' in keys:
            win.close()
            core.quit()

    rt = rt_clock.getTime()
    resp_key = keys[0]

    # Logic
    chosen_idx = -1
    correct_idx = -1
    for idx, item in enumerate(layout_config):
        if resp_key in item['keys']: chosen_idx = idx
        if item['ang'] == target_angle: correct_idx = idx
            
    is_correct = 1 if chosen_idx == correct_idx else 0

    # Feedback
    if chosen_idx != -1:
        if is_correct:
            target_circles[chosen_idx].lineColor = 'lime'
            target_circles[chosen_idx].lineWidth = 4
        else:
            target_circles[chosen_idx].lineColor = 'red'
            target_circles[chosen_idx].lineWidth = 4
            target_circles[correct_idx].lineColor = 'lime'
            target_circles[correct_idx].lineWidth = 4
            
            cx, cy = target_pos
            correction_text.pos = (cx * 1.2, cy * 1.2)

    rt_text.text = f"{rt:.3f} s"
    rt_text.color = 'cyan' if rt < 0.5 else ('white' if rt < 1.5 else 'orange')

    # Animation
    for _ in range(60):
        for circ, lbl in zip(target_circles, target_labels):
            circ.draw()
            lbl.draw()
        if not is_correct:
            correction_text.draw()
        dots.draw()
        rt_text.draw()
        progress_text.draw()
        win.flip()

    return {
        'RT': rt,
        'Response': resp_key,
        'Correct': is_correct,
        'Coherence': coherence,
        'TargetAngle': target_angle
    }

intro_txt = (f"欢迎参加实验\n\n"
             f"练习阶段 ({N_PRACTICE}次)\n"
             f"请根据圆圈旁的标签选择按键\n\n"
             f"左手: Q W E A D Z X C\n右手: 小键盘 7 9 4 6 1 3\n\n"
             f"按空格键开始")

visual.TextStim(win, text=intro_txt, color='white', height=24).draw()
win.flip()
event.waitKeys(keyList=['space'])

practice_trials = []
for i in range(N_PRACTICE):
    cfg = random.choice(layout_config)
    coh = random.choice(COHERENCE_LEVELS)
    practice_trials.append({'cfg': cfg, 'coh': coh})

for i, trial in enumerate(practice_trials):
    prog_str = f"练习: {i+1} / {N_PRACTICE}"
    run_single_trial(
        target_angle=trial['cfg']['ang'],
        coherence=trial['coh'],
        correct_keys=trial['cfg']['keys'],
        target_pos=trial['cfg']['pos'],
        progress_str=prog_str
    )

visual.TextStim(win, text="练习结束！\n按空格键开始【正式实验】", color='cyan', height=24).draw()
win.flip()
event.waitKeys(keyList=['space'])

main_trial_list = []
for item in layout_config:
    for coh in COHERENCE_LEVELS:
        main_trial_list.append({
            'target_angle': item['ang'],
            'correct_keys': item['keys'],
            'coherence': coh,
            'target_pos': item['pos']
        })

trials = data.TrialHandler(trialList=main_trial_list, nReps=N_REPS_MAIN, method='random')
this_exp.addLoop(trials)

total_main_trials = trials.nTotal

for trial in trials:
    prog_str = f"正式实验: {trials.thisN + 1} / {total_main_trials}"
    res = run_single_trial(
        target_angle=trial['target_angle'],
        coherence=trial['coherence'],
        correct_keys=trial['correct_keys'],
        target_pos=trial['target_pos'],
        progress_str=prog_str
    )
    
    trials.addData('RT', res['RT'])
    trials.addData('Response', res['Response'])
    trials.addData('Correct', res['Correct'])
    trials.addData('Coherence', res['Coherence'])
    trials.addData('TargetAngle', res['TargetAngle'])
    this_exp.nextEntry()

visual.TextStim(win, text="所有实验结束\n感谢您的参与！", color='white', height=24).draw()
win.flip()
core.wait(2.0)
win.close()
core.quit()