import cv2
import math
from time import sleep
from datetime import datetime
from random import random
import numpy as np
import pyautogui
from pymouse import PyMouse
from pykeyboard import PyKeyboard, PyKeyboardEvent


def print_msg(msg):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('{}:  {}'.format(current_time, msg))


class OnKeyboardEvent(PyKeyboardEvent):
    def __init__(self):
        PyKeyboardEvent.__init__(self)
        self.input = ""

    def tap(self, keycode, character, press):
        if press:
            global is_running
            if character in ['q', 'Q']:
                self.stop()
                print_msg('Exit!')
                exit(0)
            if character in ['r', 'R']:
                is_running = not is_running
                if is_running:
                    print_msg('Run!')
                else:
                    print_msg('Stop!')
            if character in ['s', 'S']:
                print_msg('Test!')


def read_screenshot(save_path=None):
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    if save_path is not None:
        cv2.imwrite(save_path, img)
    return img


def find_buttons(img, templ, multi_scales=None):
    points_and_scores = []
    if not multi_scales:
        res_map = cv2.matchTemplate(img, templ, cv2.TM_CCOEFF_NORMED)  # -1.0 ~ 1.0
        points = np.where(res_map >= THRES_LOC)
        scores = res_map[points]
        for row, col, s in zip(*points, scores):
            point = (row + templ.shape[0]//2, col + templ.shape[1]//2)
            points_and_scores.append((point, s))
    else:
        for scale in multi_scales:
            scaled_size = (int(templ.shape[1] * scale), int(templ.shape[0] * scale))
            if scale < 1.0:
                templ_resized = cv2.resize(templ, scaled_size, cv2.INTER_AREA)
            elif scale > 1.0:
                templ_resized = cv2.resize(templ, scaled_size, cv2.INTER_LINEAR)
            else:
                templ_resized = templ
            res_map = cv2.matchTemplate(img, templ_resized, cv2.TM_CCOEFF_NORMED)  # -1.0 ~ 1.0
            points = np.where(res_map >= THRES_LOC)
            scores = res_map[points]
            for row, col, s in zip(*points, scores):
                point = (row + templ_resized.shape[0] // 2, col + templ_resized.shape[1] // 2)
                points_and_scores.append((point, s))
    points_and_scores = sorted(points_and_scores, key=lambda x: x[1])
    return np.array(points_and_scores)


def calc_distances(pt1, pt2):
    d_x = pt1[0] - pt2[0]
    d_y = pt1[1] - pt2[1]
    return math.sqrt(d_x**2 + d_y**2)


def NMS(points_and_scores):
    picked_points = []
    while len(points_and_scores) > 0:
        point1 = points_and_scores[-1][0]
        picked_points.append(point1)
        dists = np.array([calc_distances(point1, point2) for point2, _ in points_and_scores[:-1]])
        keep_indices = np.where(dists > THRES_NMS)
        points_and_scores = points_and_scores[keep_indices]
    return picked_points


def draw_picked_pts(save_path):
    for _pt in picked_pts:
        _pt = _pt[::-1]
        cv2.rectangle(src, _pt, (_pt[0] + button.shape[1], _pt[1] + button.shape[0]), (0, 0, 255), 2)
    cv2.imwrite(save_path, src)


if __name__ == '__main__':

    # Params
    template_path = './resources/button.bmp'
    THRES_LOC = 0.6
    THRES_NMS = 30
    MULTI_SCALES = None  # (0.5, 0.75, 1.0, 1.5, 2.0)
    THRES_TIME_DELAY, THRES_TIME_DELAY_RAND_RATE = 0.5, 0.2
    THRES_TIME_CLICK, THRES_TIME_CLICK_RAND_RATE = 0.5, 0.2
    THRES_SCROLL_VERTICAL = -4
    THRES_MAX_CLICK = None

    # Init Vars
    is_running = False
    count_click = 0
    button = cv2.imread(template_path)

    # Init Mouse
    m = PyMouse()
    print("[INFO] Press 'r' to Run/Stop")
    print("[INFO] Press 'q' to Exit")
    print('[INFO] Screen Size: {}'.format(m.screen_size()))

    # Init Keyboard
    kb = PyKeyboard()
    kb_event = OnKeyboardEvent()
    kb_event.start()

    # Loop

    while 1:
        if is_running:
            # Read screen
            src = read_screenshot()
            print_msg('Read screen!')
            # Detect
            picked_pts = NMS(find_buttons(src, button, MULTI_SCALES))
            if picked_pts:
                # Move and Click
                print_msg('Found {} buttons! Move and click...'.format(len(picked_pts)))
                for pt in picked_pts:
                    pt_x, pt_y = pt[1].item(), pt[0].item()
                    m.move(pt_x, pt_y)
                    m.click(pt_x, pt_y, button=1, n=1)
                    count_click += 1
                    sleep(THRES_TIME_CLICK + THRES_TIME_CLICK_RAND_RATE * random())
                # draw_picked_pts()
            else:
                # Scroll
                print_msg('Found no buttons! Scroll...')
                m.scroll(vertical=THRES_SCROLL_VERTICAL)
        elif THRES_MAX_CLICK is None:
            THRES_MAX_CLICK = int(input("Please input THRES_MAX_CLICK: "))
            THRES_MAX_CLICK = max(0, THRES_MAX_CLICK)
            print('Set THRES_MAX_CLICK to {}'.format(THRES_MAX_CLICK))
        # Delay
        sleep(THRES_TIME_DELAY + THRES_TIME_DELAY_RAND_RATE * random())
        # Check running state
        if count_click >= THRES_MAX_CLICK:
            count_click = 0
            THRES_MAX_CLICK = None
            is_running = False
