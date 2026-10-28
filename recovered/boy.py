from math import pi
from pico2d import load_image, get_time, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.last_updated_at = get_time()
        self.idle_started_at = self.last_updated_at
        self.frame = 0
        self.face_dir = 1
        self.direction = 0
        self.pressed_keys = []
        self.image = load_image('animation_sheet.png')
        self.state_machine = Machine(
            model=self, states=['RUN', {'name': 'IDLE', 'on_enter': '_enter_idle'}, {'name': 'SLEEP', 'on_enter': '_enter_sleep'}], initial='IDLE', auto_transitions=False,
            transitions=[{'trigger': 'start_running', 'source': 'IDLE', 'dest': 'RUN'},
                         {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                         {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
                         {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                         {'trigger': 'animate', 'source': 'IDLE', 'dest': None,
                          'after': '_animate_idle'}])

    def update(self):
        now = get_time()
        elapsed = max(0.0, now - self.last_updated_at)
        self.last_updated_at = now
        if self.state == 'IDLE':
            if get_time() - self.idle_started_at >= 5.0:
                self.fall_asleep()
            else:
                self.animate()

        elif self.state == 'RUN':
            self.x += self.direction * 200.0 * elapsed
            self._animate_idle()

    def _animate_idle(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
        else:
            row = 300 if self.face_dir == 1 else 200
        if self.state == 'SLEEP':
            angle = pi / 2 if self.face_dir == 1 else -pi / 2
            self.image.clip_composite_draw(0, row, 100, 100, angle, '',
                                           self.x, self.y - 15, 100, 100)
        else:
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)

    def _enter_idle(self):
        self.idle_started_at = get_time()
        self.frame = 0

    def handle_event(self, event):
        if self.state != 'SLEEP':
            self._handle_direction(event)
        if (self.state == 'SLEEP' and event.type == SDL_KEYDOWN
                and event.key == SDLK_SPACE):
            self.wake_up()

    def _enter_sleep(self):
        self.frame = 0

    def _handle_direction(self, event):
        if event.type == SDL_KEYUP and event.key in self.pressed_keys:
            self.pressed_keys.remove(event.key)
            if not self.pressed_keys:
                self.direction = 0
                if self.state == 'RUN':
                    self.stop_running()
            else:
                self.direction = 1 if self.pressed_keys[-1] == SDLK_RIGHT else -1
                self.face_dir = self.direction
            return
        if event.type != SDL_KEYDOWN or event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return
        if event.key not in self.pressed_keys:
            self.pressed_keys.append(event.key)
        self.direction = 1 if self.pressed_keys[-1] == SDLK_RIGHT else -1
        self.face_dir = self.direction
        if self.state == 'IDLE':
            self.start_running()
