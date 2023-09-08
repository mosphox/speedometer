from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.animation import Animation
from kivy.config import Config

import time, math, psutil, ctypes

from threading import Thread
from functools import partial

ctypes.windll.shcore.SetProcessDpiAwareness(True)

Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '600')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

Builder.load_file("layout.kv")

class GetSpeed():
    def __init__(self):
        self.speed = [0, 0]
        self.timeout = time.time()

        self.memory = [0, 0]
        self.memory_timeout = time.time()

        self.size = [0, 0]
        self.size_timeout = time.time()

        self.process()

    def process(self):

        def daemon():
            time.sleep(1.5)
            
            while True:
                speed = max(psutil.cpu_percent(percpu = True)) * 1000

                self.speed[0] = self.speed[1]
                self.speed[1] = speed

                self.timeout = time.time()

                memory = psutil.virtual_memory().percent * 1000

                self.memory[0] = self.memory[1]
                self.memory[1] = memory

                self.memory_timeout = time.time()

                size = psutil.disk_usage('/').percent * 1000

                self.size[0] = self.size[1]
                self.size[1] = size

                self.size_timeout = time.time()

                time.sleep(1)
                
        thread = Thread(target = daemon)
        thread.daemon = True
        thread.start()

class WatchFace(FloatLayout):
    def getram(self):
        return " / (" + str(round(psutil.virtual_memory().total / 1024 ** 3, 2)) + " GB)"

    def getdisk(self):
        return " / (" + str(round(psutil.disk_usage('/').total / 1024 ** 3, 2)) + " GB)"

class FigureLabel(FloatLayout):
    label_text = StringProperty()
    label_pos = NumericProperty()
    label_color = ListProperty([0, 0, 0])

    def __init__(self, label_text, label_pos, label_color, **kwargs):
        super().__init__(**kwargs)
        self.label_text = label_text
        self.label_pos = label_pos - 5
        self.label_color = label_color

    def change_color(self, color):
        self.label_color = color

class Circle(FloatLayout):
    color = ListProperty([1, 1, 1])
    multiplier = NumericProperty()

    def __init__(self, color, multiplier, **kwargs):
        super().__init__(**kwargs)

        self.color = color
        self.multiplier = multiplier

class Lines(FloatLayout):
    value = NumericProperty()
    length = NumericProperty()
    angle = NumericProperty()
    corrector = NumericProperty()
    radius = NumericProperty()
    color = ListProperty([0, 0, 0])

    def __init__(self, color, length, angle, corrector, radius, value, **kwargs):
        super().__init__(**kwargs)

        self.value = value
        self.length = length
        self.color = color
        self.angle = angle
        self.corrector = corrector
        self.radius = radius

    def change_color(self, color):
        self.color = color

class Ticks(Widget):
    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)

        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)

        self.speedometer = GetSpeed()

        self.update_func(initial = True)

    def update_func(self, positions = [], initial = False):
        if initial == True:
            self.previos_position = 200000
            self.previos_memory_position = 200000
            self.previos_swap_position = 200000
            self.previos_size_position = 200000

        else:
            update_list = []

            self.current_position = positions[0]
            self.current_memory_position = positions[1]
            self.current_size_position = positions[2]

            if self.previos_position > self.current_position + 500 or self.previos_position < self.current_position - 500:
                update_list.append(True)
                self.previos_position = self.current_position

            else:
                update_list.append(False)

            if self.previos_memory_position > self.current_memory_position + 833 or self.previos_memory_position < self.current_memory_position - 833:
                update_list.append(True)
                self.previos_memory_position = self.current_memory_position

            else:
                update_list.append(False)

            if self.previos_size_position > self.current_size_position + 1666 or self.previos_size_position < self.current_size_position - 1666:
                update_list.append(True)
                self.previos_size_position = self.current_size_position

            else:
                update_list.append(False)

            return update_list

    def update_clock(self, clock, *args):
        self.canvas.clear()

        self.position = min((self.speedometer.speed[0] + (self.speedometer.speed[1] - self.speedometer.speed[0]) * ((time.time() - self.speedometer.timeout) ** 0.7)), 100000)
        self.memory_position = min((self.speedometer.memory[0] + (self.speedometer.memory[1] - self.speedometer.memory[0]) * ((time.time() - self.speedometer.memory_timeout) ** 0.7)), 100000)
        self.size_position = min((self.speedometer.size[0] + (self.speedometer.size[1] - self.speedometer.size[0]) * ((time.time() - self.speedometer.size_timeout) ** 0.7)), 100000)

        update_list = self.update_func([self.position, self.memory_position, self.size_position])

        if update_list[0] == True:
            [item.change_color([0, 220 / 255, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value < self.position / 500 and item.value < 40) else
             item.change_color([220 / 255, 0, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value < self.position / 500 and item.value > 160) else
             item.change_color([220 / 255, 220 / 255, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value < self.position / 500) else
             item.change_color([17 / 255, 92 / 255, 37 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value > self.position / 500 and item.value < 40) else 
             item.change_color([92 / 255, 17 / 255, 17 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value > self.position / 500 and item.value > 160) else 
             item.change_color([92 / 255, 78 / 255, 17 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 2.52 / 2 and item.value > self.position / 500) else 
             None for item in clock.children]

            [item.change_color([0, 220 / 255, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value < self.position / 2000 and item.value < 10) else
             item.change_color([220 / 255, 0, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value < self.position / 2000 and item.value > 40) else
             item.change_color([220 / 255, 220 / 255, 0]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value < self.position / 2000) else
             item.change_color([17 / 255, 92 / 255, 37 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value > self.position / 2000 and item.value < 10) else 
             item.change_color([92 / 255, 17 / 255, 17 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value > self.position / 2000 and item.value > 40) else 
             item.change_color([92 / 255, 78 / 255, 17 / 255]) if (type(item) == Lines and item.radius == 0.9 and item.angle == 5.04 and item.value > self.position / 2000) else 
             None for item in clock.children]

        if update_list[1] == True:
            [item.change_color([(26 + item.value + 109) / 255, 165 / 255, 196 / 255]) if (type(item) == Lines and item.radius == 0.55 and item.angle == 2.1 and item.value < self.memory_position / 833) else
             item.change_color([(26 + item.value) / 255, 56 / 255, 87 / 255]) if (type(item) == Lines and item.radius == 0.55 and item.angle == 2.1 and item.value > self.memory_position / 833) else 
             None for item in clock.children]

            [item.change_color([(26 + item.value * 4 + 109) / 255, 165 / 255, 196 / 255]) if (type(item) == Lines and item.radius == 0.55 and item.angle == 8.4 and item.value < self.memory_position / 3333) else
             item.change_color([(26 + item.value * 4) / 255, 56 / 255, 87 / 255]) if (type(item) == Lines and item.radius == 0.55 and item.angle == 8.4 and item.value > self.memory_position / 3333) else 
             None for item in clock.children]

        if update_list[2] == True:
            [item.change_color([255 / 255, (122 - item.value * 2 + 100) / 255, 100 / 255]) if (type(item) == Lines and item.radius == 0.27 and item.angle == 4.2 and item.value < self.size_position / 1633) else
             item.change_color([200 / 255, (122 - item.value * 2) / 255, 0]) if (type(item) == Lines and item.radius == 0.27 and item.angle == 4.2 and item.value > self.size_position / 1633) else 
             None for item in clock.children]

        if update_list[0] == True:
            [(Animation.cancel_all(item), Animation(label_color = [1, 1, 1], duration = .15).start(item)) 
             if type(item) == FigureLabel and self.position - (item.label_pos + 5) * 10000 < 5000 
             and (item.label_pos + 5) * 10000 - self.position < 5000 and item.label_color == [70 / 255, 70 / 255, 70 / 255] else 
             (Animation.cancel_all(item), Animation(label_color = [70 / 255, 70 / 255, 70 / 255], duration = .15).start(item)) 
             if type(item) == FigureLabel and (self.position - (item.label_pos + 5) * 10000 > 5000 
             or (item.label_pos + 5) * 10000 - self.position > 5000) and item.label_color == [1, 1, 1] else None for item in clock.children]

            [(Animation.cancel_all(item), Animation(color = [200 / 255, 60 / 255, 60 / 255], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.9 and item.angle == 25.2 and self.position - (item.value) * 10000 < 5000 
             and (item.value) * 10000 - self.position < 5000 and item.color == [1, 1, 1] else 
             (Animation.cancel_all(item), Animation(color = [1, 1, 1], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.9 and item.angle == 25.2 and (self.position - (item.value) * 10000 > 5000 
             or (item.value) * 10000 - self.position > 5000) and item.color == [200 / 255, 60 / 255, 60 / 255] 
             else None for item in clock.children]

        if update_list[1] == True:
            [(Animation.cancel_all(item), Animation(color = [60 / 255, 60 / 255, 200 / 255], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.55 and item.angle == 25.2 and self.memory_position - (item.value) * 10000 < 5000 
             and (item.value) * 10000 - self.memory_position < 5000 and item.color == [1, 1, 1] else 
             (Animation.cancel_all(item), Animation(color = [1, 1, 1], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.55 and item.angle == 25.2 and (self.memory_position - (item.value) * 10000 > 5000 
             or (item.value) * 10000 - self.memory_position > 5000) and item.color == [60 / 255, 60 / 255, 200 / 255] 
             else None for item in clock.children]

        if update_list[2] == True:
            [(Animation.cancel_all(item), Animation(color = [200 / 255, 200 / 255, 60 / 255], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.27 and item.angle == 25.2 and self.size_position - (item.value) * 10000 < 5000 
             and (item.value) * 10000 - self.size_position < 5000 and item.color == [1, 1, 1] else 
             (Animation.cancel_all(item), Animation(color = [1, 1, 1], duration = .15).start(item)) 
             if type(item) == Lines and item.radius == 0.27 and item.angle == 25.2 and (self.size_position - (item.value) * 10000 > 5000 
             or (item.value) * 10000 - self.size_position > 5000) and item.color == [200 / 255, 200 / 255, 60 / 255] 
             else None for item in clock.children]
        
        with self.canvas:

            Color(200 / 255, 60 / 255, 60 / 255)
            Line(points = [self.center_x + 0.59 * self.radius * 0.993 * math.sin(360 / 100000 * (self.position * 0.7 - 35000) * math.pi / 180), self.center_y + 0.59 * self.radius * 0.993 * math.cos(360 / 100000 * (self.position * 0.7 - 35000) * math.pi / 180), self.center_x + 0.9 * self.radius * 0.993 * math.sin(360 / 100000 * (self.position * 0.7 - 35000) * math.pi / 180), self.center_y + 0.9 * self.radius * 0.993 * math.cos(360 / 100000 * (self.position * 0.7 - 35000) * math.pi / 180)], width = min(self.size) / 300, cap = "round")
            
            Color(60 / 255, 60 / 255, 200 / 255)
            Line(points = [self.center_x + 0.3 * self.radius * 0.993 * math.sin(360 / 100000 * (self.memory_position * 0.7 - 35000) * math.pi / 180), self.center_y + 0.3 * self.radius * 0.993 * math.cos(360 / 100000 * (self.memory_position * 0.7 - 35000) * math.pi / 180), self.center_x + 0.52 * self.radius * 0.993 * math.sin(360 / 100000 * (self.memory_position * 0.7 - 35000) * math.pi / 180), self.center_y + 0.52 * self.radius * 0.993 * math.cos(360 / 100000 * (self.memory_position * 0.7 - 35000) * math.pi / 180)], width = min(self.size) / 300, cap = "round")

            Color(200 / 255, 200 / 255, 60 / 255)
            Line(points = [self.center_x, self.center_y, self.center_x + 0.21 * self.radius * 0.993 * math.sin(360 / 100000 * (self.size_position * 0.7 - 35000) * math.pi / 180), self.center_y + 0.21 * self.radius * 0.993 * math.cos(360 / 100000 * (self.size_position * 0.7 - 35000) * math.pi / 180)], width = min(self.size) / 300, cap = "round")
            
            Color(200 / 255, 200 / 255, 60 / 255)
            Line(points = [self.center_x, self.center_y, self.center_x - 0.08 * self.radius * 0.993 * math.sin(360 / 100000 * (self.size_position * 0.7 - 35000) * math.pi / 180), self.center_y - 0.08 * self.radius * 0.993 * math.cos(360 / 100000 * (self.size_position * 0.7 - 35000) * math.pi / 180)], width = min(self.size) / 300, cap = "round")

class SpeedometerApp(App):
    icon = "assets\\icon.png"
    
    def build(self):
        clock = WatchFace()

        [clock.add_widget(FigureLabel(str(i * 10), i, [70 / 255, 70 / 255, 70 / 255]), -1) for i in range(11)]
        [clock.add_widget(Lines([1, 1, 1], 0.94, 25.2, 5, 0.9, i), -1) for i in range(11)]

        [clock.add_widget(Lines([17 / 255, 92 / 255, 37 / 255], 0.94, 5.04, 25, 0.9, i), - 1) if i < 10 else
         clock.add_widget(Lines([92 / 255, 17 / 255, 17 / 255], 0.94, 5.04, 25, 0.9, i), - 1) if i > 40 else
         clock.add_widget(Lines([92 / 255, 78 / 255, 17 / 255], 0.94, 5.04, 25, 0.9, i), - 1)for i in range(50)]

        [clock.add_widget(Lines([17 / 255, 92 / 255, 37 / 255], 0.96, 2.52 / 2, 100, 0.9, i), - 1) if i < 40 else
         clock.add_widget(Lines([92 / 255, 17 / 255, 17 / 255], 0.96, 2.52 / 2, 100, 0.9, i), - 1) if i > 160 else
         clock.add_widget(Lines([92 / 255, 78 / 255, 17 / 255], 0.96, 2.52 / 2, 100, 0.9, i), - 1)for i in range(200)]

        [clock.add_widget(Lines([0, 0, 0], 0.94, 1.26, 100, 0.55, i)) for i in range(201)]
        [clock.add_widget(Lines([(26 + i) / 255, 56 / 255, 87 / 255], 0.94, 2.1, 60, 0.55, i)) for i in range(121)]
        [clock.add_widget(Lines([(26 + i * 4) / 255, 56 / 255, 87 / 255], 0.9, 8.4, 15, 0.55, i)) for i in range(31)]
        [clock.add_widget(Lines([1, 1, 1], 0.9, 25.2, 5, 0.55, i)) for i in range(11)]

        [clock.add_widget(Lines([0, 0, 0], 0.94, 1.26, 100, 0.27, i)) for i in range(201)]
        [clock.add_widget(Lines([200 / 255, (122 - i * 2) / 255, 0], 0.88, 4.2, 30, 0.27, i)) for i in range(61)]
        [clock.add_widget(Lines([1, 1, 1], 0.82, 25.2, 5, 0.27, i)) for i in range(11)]

        clock.add_widget(Circle([200 / 255, 200 / 255, 60 / 255], 0.025))
        clock.add_widget(Circle([0, 0, 0], 0.015))

        Clock.schedule_interval(partial(clock.ticks.update_clock, clock), 1 / 60)

        return clock

if __name__ == '__main__':
    SpeedometerApp().run()