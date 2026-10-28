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
            model=self, states=['IDLE', 'SLEEP'], initial='IDLE', auto_transitions=False,
            transitions=[{'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
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
