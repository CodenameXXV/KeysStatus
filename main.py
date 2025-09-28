import tkinter as tk
from tkinter import messagebox
import threading
import time
import pystray
from PIL import Image, ImageDraw
import ctypes
from ctypes import wintypes
import sys
import os


class PopupWindow:
    """Спливаюче вікно для відображення статусу клавіш"""

    def __init__(self):
        self.window = None
        self.animation_timer = None
        self.hide_timer = None

    def create_window(self, key_name, status, is_media_key=False):
        """Створює спливаюче вікно"""
        if self.window:
            try:
                self.window.destroy()
            except:
                pass

        # Створюємо нове вікно
        self.window = tk.Toplevel()
        self.window.withdraw()  # Спочатку ховаємо

        # Налаштування вікна
        self.window.overrideredirect(True)  # Без рамки
        self.window.attributes('-topmost', True)  # Завжди зверху
        self.window.attributes('-alpha', 0.0)  # Початкова прозорість

        # Основний фрейм без рамки
        main_frame = tk.Frame(
            self.window,
            bg='#2d3748',
            relief='flat',
            bd=0
        )
        main_frame.pack(fill='both', expand=True)

        # Кольори та текст для статусу
        if is_media_key:
            # Для медіаклавіш - просто назва без символів
            status_color = '#48bb78'  # Зелений
            main_text = key_name.upper()
        else:
            # Для звичайних клавіш - з символами статусу
            if status:
                status_color = '#48bb78'  # Зелений
                status_symbol = '✅'
            else:
                status_color = '#f56565'  # Червоний
                status_symbol = '❌'
            main_text = f"{key_name.upper()} {status_symbol}"

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text=main_text,
            font=('Segoe UI', 12, 'bold'),
            fg=status_color,
            bg='#2d3748'
        )
        title_label.pack(pady=(15, 15))

        # Розташування вікна
        self.window.update_idletasks()
        width = 200
        height = 60
        self.window.geometry(f'{width}x{height}')

        # Позиція знизу по центру екрану
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = screen_height - height - 50

        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # Показуємо з анімацією
        self.show_with_animation()

        # Автоматично закриваємо через 2 секунди
        if self.hide_timer:
            self.window.after_cancel(self.hide_timer)
        self.hide_timer = self.window.after(2000, self.hide_with_animation)

    def show_with_animation(self):
        """Анімація появи"""
        self.window.deiconify()  # Показуємо вікно
        self.animate_opacity(0.0, 0.95, 15, 0.05)

    def hide_with_animation(self):
        """Анімація зникнення"""
        if self.window and self.window.winfo_exists():
            self.animate_opacity(0.95, 0.0, 15, -0.05, self.destroy_window)

    def animate_opacity(self, start, end, steps, step_size, callback=None):
        """Анімує прозорість вікна"""
        if not self.window or not self.window.winfo_exists():
            return

        current = start

        def step():
            nonlocal current
            if not self.window or not self.window.winfo_exists():
                return

            try:
                self.window.attributes('-alpha', current)
                current += step_size

                # Перевіряємо, чи досягли кінцевого значення
                if (step_size > 0 and current < end) or (step_size < 0 and current > end):
                    self.window.after(20, step)
                else:
                    # Встановлюємо точне кінцеве значення
                    self.window.attributes('-alpha', end)
                    if callback:
                        callback()
            except:
                pass

        step()

    def destroy_window(self):
        """Знищує вікно"""
        if self.window:
            try:
                self.window.destroy()
                self.window = None
            except:
                pass


class KeyboardStatusMonitor:
    """Основний клас для моніторингу статусу клавіш"""

    def __init__(self):
        self.popup = PopupWindow()
        self.tray_icon = None
        self.running = True

        # Початковий стан клавіш
        self.previous_states = {
            'num_lock': False,
            'caps_lock': False,
            'scroll_lock': False,
            'fn': False,
            'media_play_pause': False,
            'media_stop': False,
            'media_prev': False,
            'media_next': False,
            'volume_mute': False,
            'volume_down': False,
            'volume_up': False
        }

        # Створюємо root вікно (приховане)
        self.root = tk.Tk()
        self.root.withdraw()

        self.setup_tray()
        self.start_monitoring()

    def create_tray_icon(self):
        """Створює іконку для системного трея"""
        # Створюємо іконку 64x64
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Малюємо клавіатуру
        # Основа клавіатури
        draw.rectangle([8, 20, 56, 44], fill='#4a5568', outline='#2d3748', width=2)

        # Клавіші верхнього ряду
        draw.rectangle([12, 24, 18, 30], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([20, 24, 26, 30], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([28, 24, 34, 30], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([36, 24, 42, 30], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([44, 24, 50, 30], fill='#e2e8f0', outline='#cbd5e0')

        # Клавіші нижнього ряду
        draw.rectangle([12, 32, 18, 38], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([20, 32, 30, 38], fill='#e2e8f0', outline='#cbd5e0')  # Пробіл
        draw.rectangle([32, 32, 38, 38], fill='#e2e8f0', outline='#cbd5e0')
        draw.rectangle([40, 32, 46, 38], fill='#e2e8f0', outline='#cbd5e0')

        return image

    def setup_tray(self):
        """Налаштовує системний трей"""
        icon_image = self.create_tray_icon()

        # Створюємо меню
        menu = pystray.Menu(
            pystray.MenuItem("About", self.show_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_application)
        )

        # Створюємо іконку трея
        self.tray_icon = pystray.Icon(
            "KeyboardMonitor",
            icon_image,
            "Keys status monitor\nNumLock, CapsLock, ScrollLock, Fn, Media keys",
            menu
        )

    def get_key_states(self):
        """Отримує поточний стан клавіш через Windows API"""
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)

            # Коди віртуальних клавіш
            VK_NUMLOCK = 0x90
            VK_CAPITAL = 0x14
            VK_SCROLL = 0x91
            VK_FN = 0x73     # Fn (може не працювати на всіх клавіатурах)
            
            # Медіа клавіші
            VK_MEDIA_PLAY_PAUSE = 0xB3
            VK_MEDIA_STOP = 0xB2
            VK_MEDIA_PREV_TRACK = 0xB1
            VK_MEDIA_NEXT_TRACK = 0xB0
            VK_VOLUME_MUTE = 0xAD
            VK_VOLUME_DOWN = 0xAE
            VK_VOLUME_UP = 0xAF

            # Отримуємо стан клавіш
            num_lock = bool(user32.GetKeyState(VK_NUMLOCK) & 1)
            caps_lock = bool(user32.GetKeyState(VK_CAPITAL) & 1)
            scroll_lock = bool(user32.GetKeyState(VK_SCROLL) & 1)
            fn = bool(user32.GetKeyState(VK_FN) & 0x8000)
            
            # Медіа клавіші (перевіряємо як натиснуті)
            media_play_pause = bool(user32.GetKeyState(VK_MEDIA_PLAY_PAUSE) & 0x8000)
            media_stop = bool(user32.GetKeyState(VK_MEDIA_STOP) & 0x8000)
            media_prev = bool(user32.GetKeyState(VK_MEDIA_PREV_TRACK) & 0x8000)
            media_next = bool(user32.GetKeyState(VK_MEDIA_NEXT_TRACK) & 0x8000)
            volume_mute = bool(user32.GetKeyState(VK_VOLUME_MUTE) & 0x8000)
            volume_down = bool(user32.GetKeyState(VK_VOLUME_DOWN) & 0x8000)
            volume_up = bool(user32.GetKeyState(VK_VOLUME_UP) & 0x8000)

            return {
                'num_lock': num_lock,
                'caps_lock': caps_lock,
                'scroll_lock': scroll_lock,
                'fn': fn,
                'media_play_pause': media_play_pause,
                'media_stop': media_stop,
                'media_prev': media_prev,
                'media_next': media_next,
                'volume_mute': volume_mute,
                'volume_down': volume_down,
                'volume_up': volume_up
            }
        except Exception as e:
            print(f"Помилка отримання стану клавіш: {e}")
            return self.previous_states.copy()

    def monitor_keys(self):
        """Моніторить зміни стану клавіш"""
        key_names = {
            'num_lock': 'NumLock',
            'caps_lock': 'CapsLock',
            'scroll_lock': 'ScrollLock',
            'fn': 'Fn',
            'media_play_pause': 'Play/Pause',
            'media_stop': 'Stop',
            'media_prev': 'Previous',
            'media_next': 'Next',
            'volume_mute': 'Mute',
            'volume_down': 'Vol-',
            'volume_up': 'Vol+'
        }

        while self.running:
            try:
                current_states = self.get_key_states()

                # Перевіряємо зміни
                for key, current_state in current_states.items():
                    if current_state != self.previous_states[key]:
                        # Для медіаклавіш показуємо тільки факт натискання
                        if key.startswith('media_') or key.startswith('volume_'):
                            if current_state:  # Тільки коли натиснуто
                                self.root.after(0, lambda k=key_names[key], s=True:
                                self.show_popup_status(k, s))
                        else:
                            # Для звичайних клавіш показуємо статус
                            self.root.after(0, lambda k=key_names[key], s=current_state:
                            self.show_popup_status(k, s))
                        
                        self.previous_states[key] = current_state

                time.sleep(0.1)  # Перевіряємо кожні 100мс

            except Exception as e:
                print(f"Помилка моніторингу: {e}")
                time.sleep(1)

    def show_popup_status(self, key_name, status):
        """Показує popup з статусом клавіші"""
        # Для медіаклавіш передаємо спеціальний параметр
        is_media_key = any(media in key_name.lower() for media in ['play', 'pause', 'stop', 'prev', 'next', 'mute', 'vol'])
        self.popup.create_window(key_name, status, is_media_key)

    def start_monitoring(self):
        """Запускає моніторинг в окремому потоці"""
        monitor_thread = threading.Thread(target=self.monitor_keys, daemon=True)
        monitor_thread.start()


    def show_about(self, icon=None, item=None):
        """Показує інформацію про програму"""

        def show_dialog():
            messagebox.showinfo(
                "About",
                "Monitor keyboard status v0.1\n\n"
                "• NumLock, CapsLock, ScrollLock\n"
                "• Fn (if you have one)\n"
                "• Media: Play/Pause, Stop, Prev, Next\n"
                "• Volume: Mute, Vol-, Vol+\n\n"
                "Author:\n"
                "Ihor Shuliak"
            )

        self.root.after(0, show_dialog)

    def quit_application(self, icon=None, item=None):
        """Завершує програму"""
        self.running = False

        # Закриваємо popup якщо відкритий
        if self.popup.window:
            try:
                self.popup.window.destroy()
            except:
                pass

        # Закриваємо трей
        if self.tray_icon:
            self.tray_icon.stop()

        # Закриваємо root вікно
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

        sys.exit(0)

    def run(self):
        """Запускає програму"""
        try:
            # Запускаємо іконку трея в окремому потоці
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()

            # Запускаємо головний цикл tkinter
            self.root.mainloop()

        except KeyboardInterrupt:
            self.quit_application()


def main():
    """Головна функція"""
    try:
        # Перевіряємо ОС
        if os.name != 'nt':
            print("Ця програма працює тільки на Windows")
            return 1


        # Створюємо та запускаємо монітор
        monitor = KeyboardStatusMonitor()
        monitor.run()

        return 0

    except Exception as e:
        print(f"Критична помилка: {e}")
        input("Натисніть Enter для виходу...")
        return 1


if __name__ == "__main__":
    sys.exit(main())