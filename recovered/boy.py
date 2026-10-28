from math import pi
from pico2d import (
    load_image, get_time, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a,
)
from transitions import Machine
from auto_run import AutoRun


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.direction = 0
        self.auto_run = AutoRun(self)
        self.pressed_keys = []
        self.image = load_image('animation_sheet.png')
        self.idle_started_at = get_time()
        self.last_updated_at = self.idle_started_at
        self.state_machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': '_enter_idle'},
                {'name': 'RUN', 'on_enter': '_enter_run'},
                {'name': 'AUTORUN', 'on_enter': '_enter_autorun'},
                {'name': 'SLEEP', 'on_enter': '_enter_sleep'},
            ],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                {'trigger': 'animate', 'source': ['IDLE', 'RUN', 'AUTORUN'], 'dest': None,
                 'after': '_animate'},
                {'trigger': 'start_running', 'source': ['IDLE', 'SLEEP', 'AUTORUN'], 'dest': 'RUN'},
                {'trigger': 'start_autorun', 'source': 'IDLE', 'dest': 'AUTORUN'},
                {'trigger': 'finish_autorun', 'source': 'AUTORUN', 'dest': 'IDLE'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
            ],
        )

    def _enter_idle(self):
        self.idle_started_at = get_time()
        self.frame = 0
        self.direction = 0

    def _enter_run(self):
        self.frame = 0
        self.last_updated_at = get_time()

    def _enter_autorun(self):
        self.frame = 0
        self.pressed_keys.clear()
        self.last_updated_at = get_time()
        self.auto_run.enter(self.last_updated_at)

    def _enter_sleep(self):
        self.frame = 0
        self.pressed_keys.clear()

    def handle_event(self, event):
        if (self.state == 'IDLE' and event.type == SDL_KEYDOWN
                and event.key == SDLK_a):
            self.start_autorun()
            return

        if self.state == 'SLEEP':
            if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
                self.wake_up()
                return

        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            if event.key not in self.pressed_keys:
                self.pressed_keys.append(event.key)
        elif event.key in self.pressed_keys:
            self.pressed_keys.remove(event.key)

        # When both keys are held, the most recently pressed key wins.
        if self.pressed_keys:
            self.direction = 1 if self.pressed_keys[-1] == SDLK_RIGHT else -1
            self.face_dir = self.direction
            if self.state in ('IDLE', 'SLEEP', 'AUTORUN'):
                self.start_running()
        elif self.state == 'RUN':
            self.stop_running()

    def update(self):
        now = get_time()
        elapsed = max(0.0, now - self.last_updated_at)
        self.last_updated_at = now
        if self.state == 'IDLE':
            if now - self.idle_started_at >= 5.0:
                self.fall_asleep()
            else:
                self.animate()
        elif self.state == 'RUN':
            self.x += self.direction * 200.0 * elapsed
            self.animate()

        elif self.state == 'AUTORUN':
            self.auto_run.update(now, elapsed)
            if self.state == 'AUTORUN':
                self.animate()

        # Keep the entire 100-pixel sprite inside the canvas, even when asleep.
        half_width = 75 if self.state == 'AUTORUN' else 50
        self.x = max(half_width, min(get_canvas_width() - half_width, self.x))

    def _animate(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.state in ('RUN', 'AUTORUN'):
            row = 100 if self.face_dir == 1 else 0
        else:
            row = 300 if self.face_dir == 1 else 200
        if self.state == 'AUTORUN':
            self.image.clip_draw(
                self.frame * 100, row, 100, 100, self.x, self.y + 15, 150, 150
            )
        elif self.state == 'SLEEP':
            angle = pi / 2 if self.face_dir == 1 else -pi / 2
            self.image.clip_composite_draw(
                0, row, 100, 100, angle, '', self.x, self.y - 15, 100, 100
            )
        else:
            self.image.clip_draw(
                self.frame * 100, row, 100, 100, self.x, self.y
            )
