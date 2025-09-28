<img width="294" height="255" alt="Screenshot 2025-09-28 144856" src="https://github.com/user-attachments/assets/118b71c7-fa4a-4dcc-bbac-65646fce0c2a" />


**#Keyboard Status Monitor – Display Key States with Elegant Popups**

Overview
Keyboard Status Monitor is a lightweight Windows utility that visually notifies you whenever the state of special keyboard keys changes. It shows sleek, animated popups for Num Lock, Caps Lock, Scroll Lock, Fn, and media/volume keys (Play/Pause, Stop, Previous, Next, Mute, Volume Up/Down), making it easy to track your keyboard’s current status at a glance.

Key Features

📌 Real-time monitoring of lock keys and media key presses
💡 Beautiful animated popups that appear at the bottom center of your screen with smooth fade-in/fade-out effects
🎨 Color-coded indicators: green (✅) for active/on, red (❌) for inactive/off (lock keys); clean text-only display for media keys
🖥️ Runs silently in the system tray with a custom icon — no desktop clutter
🛠️ Minimal resource usage — optimized for continuous background operation
❌ No console window — clean, user-friendly experience
🚪 Easy exit via the system tray menu
Supported Keys

Lock Keys: Num Lock, Caps Lock, Scroll Lock
Function Key: Fn (note: detection may vary by hardware)
Media Keys: Play/Pause, Stop, Previous Track, Next Track
Volume Controls: Mute, Volume Down, Volume Up
Technical Details

Built with Python, Tkinter, and pystray
Uses Windows API (user32.dll) for low-level key state detection
Fully portable — compiles to a single .exe file with PyInstaller
Works on Windows 10/11
Ideal For

Users with keyboards lacking LED indicators
Streamers and content creators who need visual feedback
Anyone who frequently toggles lock or media keys and wants instant confirmation
Author: Ihor Shuliak
License: Free for personal use

Stay in control of your keyboard — silently, stylishly, and efficiently.
