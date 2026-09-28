import random, os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Quad, Ellipse, Rectangle
from kivy.clock import Clock

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=40, spacing=15)
        l.add_widget(Label(text='НАПЁРСТКИ\nOFFLINE', font_size='36sp', bold=True, color=(1,0.8,0,1)))
        self.bal = Label(text='Баланс: 0 руб.', font_size='22sp', color=(0.2,0.9,0.2,1))
        l.add_widget(self.bal)
        b1 = Button(text='Играть', font_size='22sp', size_hint=(1,0.18))
        b1.bind(on_press=lambda x: self.go("quick"))
        b2 = Button(text='Настройки', font_size='22sp', size_hint=(1,0.18))
        b2.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        b3 = Button(text='Онлайн режим', font_size='22sp', size_hint=(1,0.18), background_color=(0.2,0.6,1,1))
        b3.bind(on_press=lambda x: self.go("tournament"))
        l.add_widget(b1); l.add_widget(b2); l.add_widget(b3); self.add_widget(l)
    def on_pre_enter(self, *a): self.bal.text = f'Баланс: {App.get_running_app().wallet} руб.'
    def go(self, mode): App.get_running_app().game_mode = mode; self.manager.current = 'game'

class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=40, spacing=15)
        l.add_widget(Label(text='НАСТРОЙКИ', font_size='32sp', bold=True))
        l.add_widget(Label(text='Автор: Иван Шестопалов', font_size='20sp', color=(1,0.5,0,1), bold=True))
        self.bd = Button(text='Сложность: СРЕДНЯЯ', font_size='20sp', size_hint=(1,0.15))
        self.bd.bind(on_press=self.ch)
        br = Button(text='Сбросить баланс', font_size='20sp', size_hint=(1,0.15), background_color=(0.8,0.2,0.2,1))
        br.bind(on_press=self.res)
        bb = Button(text='Назад', font_size='18sp', size_hint=(1,0.15))
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        l.add_widget(self.bd); l.add_widget(br); l.add_widget(Widget(size_hint=(1,0.2))); l.add_widget(bb); self.add_widget(l)
    def on_pre_enter(self, *a):
        s = App.get_running_app().shuffle_speed
        self.bd.text = f"Сложность: " + ("ВЫСОКАЯ" if s==0.4 else "НИЗКАЯ" if s==2.0 else "СРЕДНЯЯ")
    def ch(self, inst):
        a = App.get_running_app()
        a.shuffle_speed = 0.4 if a.shuffle_speed==1.0 else 2.0 if a.shuffle_speed==0.4 else 1.0
        self.on_pre_enter()
    def res(self, inst):
        a = App.get_running_app(); a.wallet = 0
        with open(a.save_file, 'w') as f: f.write('0')
        inst.text = "Сброшено!"
        Clock.schedule_once(lambda dt: setattr(inst, 'text', 'Сбросить баланс'), 2.0)

class GameCanvas(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.winning_cup = self.chosen_cup = None; self.game_state = "intro"
        self.bind(size=self.ds, pos=self.ds)
    def ds(self, *a):
        self.canvas.clear()
        with self.canvas:
            cx, cy = self.center_x, self.top - 130
            Color(0.4, 0.7, 0.3, 1); Rectangle(pos=(cx-60, cy-60), size=(120,80))
            Color(0.8, 0.3, 0.6, 1); Rectangle(pos=(cx-55, cy+20), size=(110,50))
            Color(1,1,1,1); Rectangle(pos=(cx-35, cy+35), size=(70,20))
            Color(0,0,0,1); Ellipse(pos=(cx-20, cy+42), size=(6,6)); Ellipse(pos=(cx+10, cy+42), size=(6,6))
            p = [self.width * 0.22, self.width * 0.5, self.width * 0.78]
            for i, x in enumerate(p):
                if self.game_state == "reveal" and i == self.winning_cup:
                    Color(1,0.1,0.1,1); Ellipse(pos=(x-18, self.y+40), size=(36,36))
                if self.game_state == "reveal":
                    Color(0.2,0.8,0.2,1) if i==self.winning_cup else Color(0.8,0.2,0.2,1) if i==self.chosen_cup else Color(0.6,0.4,0.3,1)
                else: Color(0.6,0.4,0.3,1)
                yb = self.y + 30 + (60 if self.game_state == "reveal" and i == self.winning_cup else 0)
                yt = yb + 130
                Quad(points=[x-55, yb, x+55, yb, x+36, yt, x-36, yt])
                Color(0.4,0.2,0.1,1); Rectangle(pos=(x-50, yb+20), size=(100,8))
    def on_touch_down(self, touch):
        if self.game_state != "playing": return super().on_touch_down(touch)
        p = [self.width * 0.22, self.width * 0.5, self.width * 0.78]
        for i, x in enumerate(p):
            if x - 60 < touch.x < x + 60 and self.y < touch.y < self.y + 180:
                self.parent.parent.check_cup(i); return True
        return super().on_touch_down(touch)

class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.winning_cup = None; self.st = ["Четвертьфинал", "Полуфинал", "ФИНАЛ!"]; self.idx = 0
        rl = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.ml = Label(text="", font_size='20sp', bold=True, size_hint=(1, 0.08), color=(1,0.5,0,1))
        self.sl = Label(text='', font_size='16sp', size_hint=(1, 0.08), halign='center')
        self.gc = GameCanvas(size_hint=(1, 0.69))
        bl = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        self.bs = Button(text='Перемешать', font_size='18sp', background_color=(0.2,0.8,0.2,1))
        self.bs.bind(on_press=self.shuffle)
        bb = Button(text='В меню', font_size='18sp', size_hint=(0.4,1))
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        bl.add_widget(self.bs); bl.add_widget(bb); rl.add_widget(self.ml); rl.add_widget(self.sl); rl.add_widget(self.gc); rl.add_widget(bl)
        self.add_widget(rl)
    def on_enter(self, *a):
        self.bs.disabled = False; self.gc.game_state = "intro"; self.gc.ds()
        if App.get_running_app().game_mode == "tournament":
            self.idx = 0; self.ml.text = f"Турнир: {self.st[self.idx]}"
            self.sl.text = 'Нажмите "Перемешать"!'
        else: self.ml.text = "Тренировка"; self.sl.text = 'Нажмите "Перемешать"!'
    def shuffle(self, inst):
        self.sl.text = 'Ниндзя перемешивает...'; self.gc.game_state = "shuffling"; self.gc.ds()
        Clock.schedule_once(self.fin, App.get_running_app().shuffle_speed)
    def fin(self, dt):
        self.winning_cup = random.randint(0, 2); self.gc.winning_cup = self.winning_cup
        self.gc.game_state = "playing"; self.gc.ds(); self.sl.text = 'Где шарик?'
    def check_cup(self, c_idx):
        if self.winning_cup is None: return
        self.gc.chosen_cup = c_idx; self.gc.game_state = "reveal"; self.gc.ds(); app = App.get_running_app()
        if c_idx == self.winning_cup:
            if app.game_mode == "tournament":
                if self.idx == 0:
                    self.idx = 1; self.ml.text = f"Турнир: {self.st[self.idx]}"
                    self.sl.text = '🎉 Пройдено! +100 руб!\nЖми Перемешать.'; app.add_money(100)
                elif self.idx == 1:
                    self.idx = 2; self.ml.text = f"Турнир: {self.st[self.idx]}"
                    self.sl.text = '🎉 Пройдено! +500 руб!\nЖми Перемешать!'; app.add_money(500)
                elif self.idx == 2:
                    self.sl.text = '🏆 ЧЕМПИОН! +1000 руб!'; app.add_money(1000); self.bs.disabled = True
            else: self.sl.text = '🎉 Угадал!'
        else:
            self.sl.text = '❌ Вылетел!' if app.game_mode == "tournament" else '❌ Мимо!'
            self.bs.disabled = True
        self.winning_cup = None

class ThimblesApp(App):
    def build(self):
        self.save_file = os.path.join(self.user_data_dir, 'wallet.txt')
        self.wallet = self.load_money(); self.game_mode = "quick"; self.shuffle_speed = 1.0
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu')); sm.add_widget(GameScreen(name='game')); sm.add_widget(SettingsScreen(name='settings'))
        return sm
    def load_money(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                try: return int(f.read())
                except: return 0
        return 0
    def add_money(self, am):
        self.wallet += am
        with open(self.save_file, 'w') as f: f.write(str(self.wallet))

if __name__ == '__main__': ThimblesApp().run()

