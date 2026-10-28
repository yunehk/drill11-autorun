from pico2d import get_canvas_width


class AutoRun:
    SPEED = 400.0
    DURATION = 5.0
    HALF_WIDTH = 75

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0

    def enter(self, now):
        self.started_at = now
        self.boy.direction = self.boy.face_dir
        self.boy.x = max(self.HALF_WIDTH, min(
            get_canvas_width() - self.HALF_WIDTH, self.boy.x))

    def update(self, now, elapsed):
        if now - self.started_at >= self.DURATION:
            self.boy.finish_autorun()
            return

        left = self.HALF_WIDTH
        right = get_canvas_width() - self.HALF_WIDTH
        span = right - left
        if span <= 0:
            self.boy.x = get_canvas_width() / 2
            return
        # Unfold the bounce path, then reflect it back into the screen.
        # This also handles crossing several edges during a slow frame.
        offset = self.boy.x - left
        phase = offset if self.boy.direction == 1 else 2 * span - offset
        phase = (phase + self.SPEED * elapsed) % (2 * span)
        if phase < span:
            self.boy.x = left + phase
            self.boy.direction = 1
        else:
            self.boy.x = right - (phase - span)
            self.boy.direction = -1
        self.boy.face_dir = self.boy.direction
