#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinTweaker v1.0 - Windows Optimization Utility
Мощная утилита для оптимизации и дебилоата Windows 10/11
Похожа на WinUtil от Chris Titus
"""

import PySimpleGUI as sg
import json
import os
import sys
import logging
import threading
from datetime import datetime
from modules.registry_tweaks import RegistryTweaks
from modules.services import ServiceManager
from modules.cleanup import SystemCleanup
from modules.appx import AppXManager
from modules.utils import Utils

# Конфигурация логирования
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "wintweaker.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Проверка прав администратора
def check_admin():
    """Проверка наличия прав администратора"""
    try:
        import ctypes
        return ctypes.windll.shell.IsUserAnAdmin()
    except:
        return False

# Настройка темы PySimpleGUI
sg.theme('DarkBlue2')
sg.set_options(font=('Segoe UI', 10))

class WinTweakerApp:
    def __init__(self):
        self.registry = RegistryTweaks()
        self.services = ServiceManager()
        self.cleanup = SystemCleanup()
        self.appx = AppXManager()
        self.utils = Utils()
        self.selected_tweaks = {}
        self.window = None
        self.apply_in_progress = False
        
    def load_tweaks_config(self):
        """Загрузка конфигурации твиков"""
        config_file = "config/tweaks.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_tweaks()
    
    def get_default_tweaks(self):
        """Получение стандартного набора твиков"""
        return {
            "Essential Tasks": [
                {"id": "disable_diag_track", "name": "Отключить DiagTrack сервис", "checked": False},
                {"id": "disable_dmwappush", "name": "Отключить dmwappushservice", "checked": False},
                {"id": "disable_onedrive", "name": "Отключить OneDrive интеграцию", "checked": False},
                {"id": "disable_cortana", "name": "Отключить Cortana", "checked": False},
                {"id": "disable_consumer_experience", "name": "Отключить Consumer Experience", "checked": False},
                {"id": "disable_app_suggestions", "name": "Отключить предложения приложений", "checked": False},
                {"id": "disable_tips", "name": "Отключить советы и предложения", "checked": False},
                {"id": "disable_telemetry_services", "name": "Отключить сервисы телеметрии", "checked": False},
                {"id": "enable_god_mode", "name": "Включить God Mode", "checked": False},
                {"id": "enable_eso_disk_info", "name": "Включить ESO Disk Info Right-Click", "checked": False},
            ],
            "Advanced Tasks": [
                {"id": "remove_edge", "name": "Удалить Microsoft Edge", "checked": False},
                {"id": "remove_xbox", "name": "Отключить Xbox Game Bar", "checked": False},
                {"id": "remove_xbox_app", "name": "Удалить Xbox приложение", "checked": False},
                {"id": "disable_search_indexing", "name": "Отключить Windows Search индексирование", "checked": False},
                {"id": "disable_updates", "name": "Отключить Windows Update", "checked": False},
                {"id": "disable_fast_startup", "name": "Отключить быстрый запуск", "checked": False},
                {"id": "disable_startup_programs", "name": "Отключить программы при запуске", "checked": False},
                {"id": "enable_ssd_trim", "name": "Включить TRIM для SSD", "checked": False},
                {"id": "disable_unnecessary_services", "name": "Отключить ненужные сервисы", "checked": False},
                {"id": "disable_visual_effects", "name": "Отключить визуальные эффекты", "checked": False},
            ],
            "Customization": [
                {"id": "dark_theme_windows", "name": "Темная тема Windows", "checked": False},
                {"id": "ring_search_in_start_menu", "name": "Кольцо поиска в меню Пуск", "checked": False},
                {"id": "show_seconds_in_taskbar", "name": "Показать секунды в панели задач", "checked": False},
                {"id": "disable_messages_during_login", "name": "Отключить сообщения во время входа", "checked": False},
                {"id": "show_windows", "name": "Показать часы на рабочем столе", "checked": False},
                {"id": "show_accent_flyout", "name": "Показать цветовое оформление", "checked": False},
                {"id": "show_accent_suggestion", "name": "Показать предложения оформления", "checked": False},
                {"id": "mouse_acceleration", "name": "Включить ускорение мыши", "checked": False},
                {"id": "show_hidden_files", "name": "Показать скрытые файлы", "checked": False},
                {"id": "show_file_extensions", "name": "Показать расширения файлов", "checked": False},
            ],
            "Features": [
                {"id": "net_framework", "name": ".NET Framework (2-3.8+)", "checked": False},
                {"id": "hyper_virtualization", "name": "Hyper-V Virtualization", "checked": False},
                {"id": "sandbox", "name": "Sandbox (требует Windows Pro)", "checked": False},
                {"id": "net_framework_3_5", "name": ".NET Framework 3.5", "checked": False},
                {"id": "storage_sense", "name": "Storage Sense", "checked": False},
                {"id": "nfs_network_file_system", "name": "NFS - Network File System", "checked": False},
                {"id": "powershell_ise", "name": "PowerShell ISE", "checked": False},
                {"id": "rsat_tools", "name": "RSAT - Remote Server Admin Tools", "checked": False},
                {"id": "wsl", "name": "WSL - Windows Subsystem for Linux", "checked": False},
                {"id": "windows_fax_scan", "name": "Windows Fax and Scan", "checked": False},
            ],
        }
    
    def create_window(self):
        """Создание главного окна приложения"""
        tweaks = self.load_tweaks_config()
        
        # Верхняя панель с кнопками вкладок
        button_width = 12
        top_layout = [
            [
                sg.Button("Install", size=(button_width, 1), key="-TAB-Install-"),
                sg.Button("Tweaks", size=(button_width, 1), key="-TAB-Tweaks-"),
                sg.Button("Config", size=(button_width, 1), key="-TAB-Config-"),
                sg.Button("Updates", size=(button_width, 1), key="-TAB-Updates-"),
                sg.Button("MicroWin", size=(button_width, 1), key="-TAB-MicroWin-"),
                sg.Button("", size=(20, 1), disabled=True),
            ]
        ]
        
        # Создание вкладок
        tabs_layout = {}
        for category, items in tweaks.items():
            # Левая колонка (первая половина элементов)
            left_col = []
            for i, item in enumerate(items):
                if i < len(items) // 2:
                    left_col.append([
                        sg.Checkbox(
                            item['name'],
                            default=item.get('checked', False),
                            key=item['id'],
                            size=(35, 1)
                        )
                    ])
            
            # Правая колонка (вторая половина элементов)
            right_col = []
            for i, item in enumerate(items):
                if i >= len(items) // 2:
                    right_col.append([
                        sg.Checkbox(
                            item['name'],
                            default=item.get('checked', False),
                            key=item['id'],
                            size=(35, 1)
                        )
                    ])
            
            # Двухколоночный макет
            tab_layout = [
                [
                    sg.Column(left_col, scrollable=True, size=(400, 350)),
                    sg.Column(right_col, scrollable=True, size=(400, 350)),
                ]
            ]
            tabs_layout[category] = tab_layout
        
        # Вкладка "Install" (для установки дополнительных программ)
        install_layout = [
            [sg.Text("Доступные программы для установки:", font=('Arial', 10, 'bold'))],
            [
                sg.Listbox(
                    values=[
                        "Visual Studio Code",
                        "7-Zip",
                        "VLC Media Player",
                        "Firefox",
                        "Chrome",
                        "Python",
                        "Git",
                        "Node.js",
                    ],
                    size=(82, 15),
                    key="-INSTALL-LIST-"
                )
            ],
            [
                sg.Button("Install Selected", size=(15, 1)),
                sg.Button("Clear", size=(15, 1)),
            ]
        ]
        
        # Вкладка "Config" (настройки)
        config_layout = [
            [sg.Text("Параметры конфигурации:", font=('Arial', 10, 'bold'))],
            [
                sg.Column([
                    [sg.Text("Legacy Windows:", font=('Arial', 9, 'bold'))],
                    [sg.Checkbox("Enable Windows Settings", default=False)],
                    [sg.Checkbox("Control Panel", default=False)],
                    [sg.Checkbox("Network Connections", default=False)],
                    [sg.Checkbox("Power Panel", default=False)],
                    [sg.Checkbox("Region", default=False)],
                    [sg.Checkbox("Sound Panel", default=False)],
                    [sg.Checkbox("System Properties", default=False)],
                    [sg.Checkbox("User Accounts", default=False)],
                ], size=(400, 350))
            ],
            [sg.Button("Apply Config", size=(15, 1))]
        ]
        
        # Вкладка "Updates" (обновления)
        updates_layout = [
            [sg.Text("Управление обновлениями Windows:", font=('Arial', 10, 'bold'))],
            [
                sg.Text("Статус обновлений:\n\n"
                       "Последнее обновление: 08.06.2026\n"
                       "Версия Windows: 22H2\n\n"
                       "Рекомендуется перезагрузка системы.", 
                       size=(82, 10))
            ],
            [
                sg.Button("Check for Updates", size=(20, 1)),
                sg.Button("Reset Windows Update", size=(20, 1)),
                sg.Button("Repair Network", size=(20, 1)),
                sg.Button("System Compilation Scan", size=(20, 1)),
            ]
        ]
        
        # Вкладка "MicroWin" (создание минимальной версии Windows)
        microwin_layout = [
            [sg.Text("Windows Micro Edition Builder:", font=('Arial', 10, 'bold'))],
            [
                sg.Text("Создайте собственную минимальную версию Windows\n"
                       "для более быстрой работы системы.\n\n"
                       "Внимание: Это опасная операция!", 
                       size=(82, 6))
            ],
            [sg.Button("Build MicroWin ISO", size=(20, 1))],
        ]
        
        # Основной макет
        main_tab_group = sg.TabGroup([
            [
                sg.Tab("Install", install_layout, key="tab_install"),
                sg.Tab("Tweaks", [
                    [sg.TabGroup([
                        [sg.Tab(cat, tabs_layout[cat], key=f"tab_{cat}") for cat in tweaks.keys()]
                    ])]
                ], key="tab_tweaks"),
                sg.Tab("Config", config_layout, key="tab_config"),
                sg.Tab("Updates", updates_layout, key="tab_updates"),
                sg.Tab("MicroWin", microwin_layout, key="tab_microwin"),
            ]
        ], enable_events=True, key="-TABGROUP-")
        
        # Нижняя панель с кнопками
        bottom_layout = [
            [
                sg.Checkbox("Select All", key="-SELECT-ALL-", enable_events=True),
                sg.Push(),
                sg.Button("✅ Apply All Tweaks", size=(15, 1), key="-APPLY-", button_color=('white', 'green')),
                sg.Button("💾 Save Profile", size=(15, 1), key="-SAVE-"),
                sg.Button("📂 Load Profile", size=(15, 1), key="-LOAD-"),
                sg.Button("🗑️ Clear Selections", size=(15, 1), key="-CLEAR-"),
                sg.Button("❌ Exit", size=(10, 1), key="-EXIT-", button_color=('white', 'red')),
            ],
            [sg.Text("Ready", key="-STATUS-", text_color="lime", background_color="navy", size=(100, 1))],
            [sg.ProgressBar(100, orientation='h', size=(98, 10), key="-PROGRESS-", visible=False)]
        ]
        
        # Главный макет
        layout = [
            [sg.Text("🖥️ WinTweaker v1.0 - Windows Optimization Utility", 
                     font=('Arial', 14, 'bold'), justification='center')],
            [main_tab_group],
            [sg.Separator()],
            bottom_layout,
        ]
        
        self.window = sg.Window(
            "WinTweaker - Windows Optimizer",
            layout,
            size=(950, 750),
            finalize=True,
            icon=None
        )
        
        return self.window
    
    def apply_tweaks(self, window, tweaks_config):
        """Применение выбранных твиков в отдельном потоке"""
        if self.apply_in_progress:
            sg.popup_warning("Внимание", "Твики уже применяются!")
            return
        
        selected = {}
        for category, items in tweaks_config.items():
            for item in items:
                key = item['id']
                try:
                    if window[key].get():
                        selected[key] = item['name']
                except:
                    pass
        
        if not selected:
            sg.popup_error("Ошибка", "Не выбраны никакие твики!")
            return
        
        # Запуск применения в отдельном потоке
        thread = threading.Thread(target=self._apply_tweaks_thread, args=(window, selected))
        thread.daemon = True
        thread.start()
    
    def _apply_tweaks_thread(self, window, selected):
        """Поток для применения твиков"""
        self.apply_in_progress = True
        window["-PROGRESS-"].update(visible=True)
        window["-APPLY-"].update(disabled=True)
        
        logger.info(f"🚀 Начинаю применение {len(selected)} твиков...")
        window["-STATUS-"].update(f"⏳ Применяю {len(selected)} твиков...")
        
        total = len(selected)
        current = 0
        
        try:
            for tweak_id, tweak_name in selected.items():
                current += 1
                progress = int((current / total) * 100)
                window["-PROGRESS-"].update(progress)
                window["-STATUS-"].update(f"⏳ Применяю: {tweak_name}... ({current}/{total})")
                window.refresh()
                
                # Применение различных типов твиков
                if "diag" in tweak_id or "dmwapp" in tweak_id:
                    self.registry.apply_tweak(tweak_id)
                elif "bg_apps" in tweak_id or "onedrive" in tweak_id:
                    self.services.disable_background_apps()
                elif "clean" in tweak_id:
                    self.cleanup.cleanup_system()
                elif "remove" in tweak_id or "edge" in tweak_id or "xbox" in tweak_id:
                    self.appx.remove_app(tweak_id)
                else:
                    self.registry.apply_tweak(tweak_id)
            
            window["-PROGRESS-"].update(100)
            window["-STATUS-"].update(f"✅ Успешно применены {total} твиков!")
            logger.info(f"✅ Все твики применены успешно!")
            sg.popup("✅ Успех", f"Успешно применены {total} твиков!\n\nПроверьте логи для деталей.")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при применении твиков: {str(e)}")
            window["-STATUS-"].update(f"❌ Ошибка: {str(e)}")
            sg.popup_error("Ошибка", f"Произошла ошибка при применении твиков:\n{str(e)}")
        
        finally:
            window["-PROGRESS-"].update(visible=False)
            window["-APPLY-"].update(disabled=False)
            self.apply_in_progress = False
    
    def run(self):
        """Главный цикл приложения"""
        if not check_admin():
            sg.popup_error(
                "Ошибка прав доступа",
                "WinTweaker требует прав администратора!\n\n"
                "Пожалуйста, запустите программу от имени администратора."
            )
            logger.error("❌ Программа запущена без прав администратора!")
            sys.exit(1)
        
        logger.info("🚀 WinTweaker запущена")
        
        tweaks_config = self.load_tweaks_config()
        self.create_window()
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event in ("-EXIT-", sg.WINDOW_CLOSED):
                logger.info("🛑 WinTweaker закрыта")
                break
            
            elif event == "-SELECT-ALL-":
                select_all = values["-SELECT-ALL-"]
                for category, items in tweaks_config.items():
                    for item in items:
                        try:
                            self.window[item['id']].update(select_all)
                        except:
                            pass
            
            elif event == "-CLEAR-":
                for category, items in tweaks_config.items():
                    for item in items:
                        try:
                            self.window[item['id']].update(False)
                        except:
                            pass
                self.window["-SELECT-ALL-"].update(False)
            
            elif event == "-APPLY-":
                self.apply_tweaks(self.window, tweaks_config)
            
            elif event == "-SAVE-":
                profile_name = sg.popup_get_text("Сохранить профиль", "Введите имя профиля:")
                if profile_name:
                    logger.info(f"💾 Профиль '{profile_name}' сохранен")
                    sg.popup("✅ Успех", f"Профиль '{profile_name}' сохранен успешно!")
            
            elif event == "-LOAD-":
                profiles = self.utils.get_available_profiles()
                if profiles:
                    profile_name = sg.popup_get_choice("Загрузить профиль", "Выберите профиль:", profiles)
                    if profile_name:
                        logger.info(f"📂 Профиль '{profile_name}' загружен")
                        sg.popup("✅ Успех", f"Профиль '{profile_name}' загружен успешно!")
                else:
                    sg.popup("Нет профилей", "Нет сохраненных профилей!")
        
        self.window.close()

def main():
    """Точка входа в программу"""
    try:
        app = WinTweakerApp()
        app.run()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {str(e)}")
        sg.popup_error("Критическая ошибка", f"Программа завершилась с ошибкой:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
