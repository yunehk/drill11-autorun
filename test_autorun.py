import unittest
from types import SimpleNamespace
from unittest.mock import patch
import boy


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        for target, kwargs in [
            ('boy.get_time', {'side_effect': lambda: self.now}),
            ('boy.load_image', {}),
            ('boy.get_canvas_width', {'return_value': 800}),
            ('auto_run.get_canvas_width', {'return_value': 800}),
        ]:
            mock = patch(target, **kwargs)
            mock.start()
            self.addCleanup(mock.stop)
        self.boy = boy.Boy()

    def key(self, code, kind=boy.SDL_KEYDOWN):
        self.boy.handle_event(SimpleNamespace(type=kind, key=code))

    def test_entry_speed_scale_timeout(self):
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.now = 0.5
        self.boy.update()
        self.assertEqual(self.boy.x, 600)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (150, 150))
        self.now = 4.999
        self.boy.update()
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.now = 5
        self.boy.update()
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.idle_started_at, 5)

    def test_both_edges_and_large_step(self):
        self.key(boy.SDLK_a)
        self.boy.x = 720
        self.now = 0.1
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.direction), (690, -1))
        self.boy.x = 80
        self.now = 0.2
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.direction), (110, 1))
        self.now = 4.9
        self.boy.update()
        self.assertTrue(75 <= self.boy.x <= 725)

    def test_cancel_each_direction_and_release(self):
        for key, direction in [(boy.SDLK_LEFT, -1), (boy.SDLK_RIGHT, 1)]:
            self.boy = boy.Boy()
            self.key(boy.SDLK_a)
            self.key(key)
            self.assertEqual((self.boy.state, self.boy.direction), ('RUN', direction))
            self.key(key, boy.SDL_KEYUP)
            self.assertEqual(self.boy.state, 'IDLE')

    def test_sleep_still_works(self):
        self.now = 5
        self.boy.update()
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(boy.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')
        self.now = 10
        self.boy.update()
        self.key(boy.SDLK_LEFT)
        self.assertEqual(self.boy.state, 'RUN')


if __name__ == '__main__':
    unittest.main()
