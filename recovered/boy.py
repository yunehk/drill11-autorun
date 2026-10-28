from pico2d import load_image, get_time, SDL_KEYDOWN, SDLK_SPACE
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.idle_started_at = get_time()
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.state_machine = Machine(
            model=self, states=[{'name': 'IDLE', 'on_enter': '_enter_idle'}, {'name': 'SLEEP', 'on_enter': '_enter_sleep'}], initial='IDLE', auto_transitions=False,
            transitions=[{'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
                         {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                         {'trigger': 'animate', 'source': 'IDLE', 'dest': None,
                          'after': '_animate_idle'}])

    def update(self):
        if self.state == 'IDLE':
            if get_time() - self.idle_started_at >= 5.0:
                self.fall_asleep()
            else:
                self.animate()

    def _animate_idle(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        row = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)

    def _enter_idle(self):
        self.idle_started_at = get_time()
        self.frame = 0

    def handle_event(self, event):
        if (self.state == 'SLEEP' and event.type == SDL_KEYDOWN
                and event.key == SDLK_SPACE):
            self.wake_up()

    def _enter_sleep(self):
        self.frame = 0
