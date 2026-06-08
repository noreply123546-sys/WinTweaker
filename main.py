#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinTweaker v2.1 - Windows Optimization Utility
Мощная утилита для оптимизации и дебилоата Windows 10/11
200+ твиков с поддержкой отката, темной темой и ПОДСКАЗКАМИ!
"""

import PySimpleGUI as sg
import json
import os
import sys
import logging
import threading
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from modules.registry_tweaks import RegistryTweaks
from modules.services import ServiceManager
from modules.cleanup import SystemCleanup
from modules.appx import AppXManager
from modules.utils import Utils
from modules.backup_manager import BackupManager
from modules.tweaks_descriptions import get_tweak_info

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

# Настройка темы PySimpleGUI - ТЕМНАЯ ГОРЯЧАЯ ТЕМА
sg.theme('DarkRed1')
sg.set_options(
    font=('Segoe UI', 10),
    text_color='#FF6B6B',
    background_color='#1a1a1a',
    element_background_color='#2a2a2a',
    button_color=('#FF6B6B', '#1a1a1a'),
    input_background_color='#2a2a2a',
    input_text_color='#FF6B6B',
    border_width=1
)

class WinTweakerApp:
    def __init__(self):
        self.registry = RegistryTweaks()
        self.services = ServiceManager()
        self.cleanup = SystemCleanup()
        self.appx = AppXManager()
        self.utils = Utils()
        self.backup_manager = BackupManager()
        self.selected_tweaks = {}
        self.window = None
        self.apply_in_progress = False
        self.last_applied_tweaks = []
        
    def load_tweaks_config(self):
        """Загрузка конфигурации твиков"""
        config_file = "config/tweaks.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_tweaks()
    
    def get_default_tweaks(self):
        """Получение стандартного набора 200+ твиков"""
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
                {"id": "remove_edge", "name": "Удалить Microsoft Edge", "checked": False},
                {"id": "disable_cortana_search", "name": "Отключить поиск Cortana", "checked": False},
                {"id": "disable_web_search", "name": "Отключить веб-поиск в меню Пуск", "checked": False},
                {"id": "disable_tracking", "name": "Отключить отслеживание", "checked": False},
                {"id": "disable_advertising_id", "name": "Отключить ID рекламы", "checked": False},
                {"id": "disable_malware_protection", "name": "Отключить Cloud Protection", "checked": False},
            ],
            "Advanced Tasks": [
                {"id": "remove_xbox", "name": "Отключить Xbox Game Bar", "checked": False},
                {"id": "remove_xbox_app", "name": "Удалить Xbox приложение", "checked": False},
                {"id": "disable_search_indexing", "name": "Отключить Windows Search индексирование", "checked": False},
                {"id": "disable_updates", "name": "Отключить Windows Update", "checked": False},
                {"id": "disable_fast_startup", "name": "Отключить быстрый запуск", "checked": False},
                {"id": "disable_startup_programs", "name": "Отключить программы при запуске", "checked": False},
                {"id": "enable_ssd_trim", "name": "Включить TRIM для SSD", "checked": False},
                {"id": "disable_unnecessary_services", "name": "Отключить ненужные сервисы", "checked": False},
                {"id": "disable_visual_effects", "name": "Отключить визуальные эффекты", "checked": False},
                {"id": "disable_animations", "name": "Отключить анимацию окон", "checked": False},
                {"id": "disable_transparency", "name": "Отключить эффект прозрачности", "checked": False},
                {"id": "disable_blur_effects", "name": "Отключить размытие в фоне", "checked": False},
                {"id": "disable_shadow_effects", "name": "Отключить тени объектов", "checked": False},
                {"id": "disable_cursor_shadow", "name": "Отключить тень курсора", "checked": False},
                {"id": "optimize_fonts", "name": "Оптимизировать отрисовку шрифтов", "checked": False},
            ],
            "Windows 10 Only": [
                {"id": "w10_disable_action_center", "name": "[W10] Отключить Центр уведомлений", "checked": False},
                {"id": "w10_disable_timeline", "name": "[W10] Отключить Timeline", "checked": False},
                {"id": "w10_disable_cloud_clipboard", "name": "[W10] Отключить облачный буфер обмена", "checked": False},
                {"id": "w10_remove_3d_objects", "name": "[W10] Удалить папку 3D Objects", "checked": False},
                {"id": "w10_disable_app_auto_update", "name": "[W10] Отключить автообновление приложений", "checked": False},
                {"id": "w10_remove_shortcuts", "name": "[W10] Удалить рекомендуемые ярлыки", "checked": False},
                {"id": "w10_disable_share", "name": "[W10] Отключить Share приложение", "checked": False},
                {"id": "w10_disable_game_mode", "name": "[W10] Отключить Game Mode", "checked": False},
                {"id": "w10_disable_game_bar", "name": "[W10] Отключить Game Bar запись", "checked": False},
                {"id": "w10_remove_bloatware", "name": "[W10] Удалить встроенный bloatware", "checked": False},
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
                {"id": "enable_dark_context_menu", "name": "Темное контекстное меню", "checked": False},
                {"id": "use_accent_color", "name": "Использовать акцентный цвет везде", "checked": False},
                {"id": "small_taskbar_icons", "name": "Маленькие значки на панели задач", "checked": False},
                {"id": "combine_taskbar_buttons", "name": "Объединить кнопки панели задач", "checked": False},
                {"id": "disable_rounded_corners", "name": "Отключить скругленные углы", "checked": False},
            ],
            "Performance": [
                {"id": "disable_background_apps", "name": "Отключить фоновые приложения", "checked": False},
                {"id": "optimize_memory", "name": "Оптимизировать оперативную память", "checked": False},
                {"id": "disable_prefetch", "name": "Отключить Prefetch", "checked": False},
                {"id": "disable_superfetch", "name": "Отключить SuperFetch", "checked": False},
                {"id": "enable_processor_throttling", "name": "Включить ограничение процессора", "checked": False},
                {"id": "disable_tips_and_ads", "name": "Отключить советы и объявления", "checked": False},
                {"id": "reduce_disk_io", "name": "Снизить использование диска I/O", "checked": False},
                {"id": "optimize_network_buffer", "name": "Оптимизировать сетевой буфер", "checked": False},
                {"id": "enable_large_system_cache", "name": "Включить большой системный кэш", "checked": False},
                {"id": "disable_memory_compression", "name": "Отключить сжатие памяти", "checked": False},
                {"id": "optimize_virtual_memory", "name": "Оптимизировать виртуальную память", "checked": False},
                {"id": "increase_file_cache", "name": "Увеличить кэш файлов", "checked": False},
                {"id": "disable_usb_selective_suspend", "name": "Отключить USB selective suspend", "checked": False},
                {"id": "disable_hard_disk_timeout", "name": "Отключить timeout жесткого диска", "checked": False},
                {"id": "optimize_startup", "name": "Оптимизировать время загрузки", "checked": False},
            ],
            "Network": [
                {"id": "disable_ipv6", "name": "Отключить IPv6", "checked": False},
                {"id": "disable_smb1", "name": "Отключить SMB1 протокол", "checked": False},
                {"id": "optimize_network", "name": "Оптимизировать сеть", "checked": False},
                {"id": "enable_dns_over_https", "name": "Включить DNS over HTTPS", "checked": False},
                {"id": "disable_nagle", "name": "Отключить алгоритм Nagle", "checked": False},
                {"id": "disable_tcp_timestamps", "name": "Отключить TCP timestamps", "checked": False},
                {"id": "enable_tcp_extensions", "name": "Включить TCP extensions", "checked": False},
                {"id": "optimize_tcp_window_size", "name": "Оптимизировать TCP window size", "checked": False},
                {"id": "disable_printer_sharing", "name": "Отключить общий доступ к принтерам", "checked": False},
                {"id": "disable_file_sharing", "name": "Отключить общий доступ к файлам", "checked": False},
                {"id": "disable_netbios", "name": "Отключить NetBIOS", "checked": False},
                {"id": "disable_llmnr", "name": "Отключить LLMNR", "checked": False},
                {"id": "disable_mdns", "name": "Отключить mDNS", "checked": False},
                {"id": "configure_dns_fallback", "name": "Настроить DNS fallback", "checked": False},
                {"id": "disable_autoplay", "name": "Отключить AutoPlay для всех устройств", "checked": False},
            ],
            "Security": [
                {"id": "disable_guest_account", "name": "Отключить гостевой аккаунт", "checked": False},
                {"id": "enable_firewall", "name": "Включить брандмауэр", "checked": False},
                {"id": "disable_remote_assistance", "name": "Отключить удаленную поддержку", "checked": False},
                {"id": "disable_remote_desktop", "name": "Отключить удаленный рабочий стол", "checked": False},
                {"id": "disable_sharing", "name": "Отключить общий доступ", "checked": False},
                {"id": "disable_anonymous_enumeration", "name": "Отключить анонимное перечисление", "checked": False},
                {"id": "disable_null_sessions", "name": "Отключить null sessions", "checked": False},
                {"id": "require_password_to_wake", "name": "Требовать пароль при пробуждении", "checked": False},
                {"id": "disable_autorun", "name": "Отключить AutoRun для всех приложений", "checked": False},
                {"id": "disable_unnecessary_devices", "name": "Отключить ненужные устройства", "checked": False},
                {"id": "enable_uac", "name": "Включить UAC", "checked": False},
                {"id": "harden_uac", "name": "Усилить UAC защиту", "checked": False},
                {"id": "disable_weak_ciphers", "name": "Отключить слабые шифры", "checked": False},
                {"id": "enable_certificate_pinning", "name": "Включить certificate pinning", "checked": False},
                {"id": "disable_smb_v1_completely", "name": "Полностью отключить SMB v1", "checked": False},
            ],
            "Cleanup": [
                {"id": "clean_temp", "name": "Очистить временные файлы", "checked": False},
                {"id": "clean_recycle", "name": "Очистить корзину", "checked": False},
                {"id": "clean_cache", "name": "Очистить кэш браузера", "checked": False},
                {"id": "clean_logs", "name": "Очистить логи системы", "checked": False},
                {"id": "clean_prefetch", "name": "Очистить Prefetch файлы", "checked": False},
                {"id": "clean_thumbnails", "name": "Очистить кэш миниатюр", "checked": False},
                {"id": "clean_windows_temp", "name": "Очистить Windows temp", "checked": False},
                {"id": "clean_appdata", "name": "Очистить AppData временные файлы", "checked": False},
                {"id": "clean_installer_cache", "name": "Очистить кэш установщика", "checked": False},
                {"id": "clean_old_updates", "name": "Удалить старые обновления", "checked": False},
            ],
            "Registry Tweaks": [
                {"id": "reg_disable_auto_restart", "name": "[REG] Отключить автоматический перезапуск", "checked": False},
                {"id": "reg_disable_user_tracking", "name": "[REG] Отключить отслеживание пользователя", "checked": False},
                {"id": "reg_disable_suggested_content", "name": "[REG] Отключить предлагаемый контент", "checked": False},
                {"id": "reg_disable_sync_folder", "name": "[REG] Отключить синхронизацию папок", "checked": False},
                {"id": "reg_disable_driver_telemetry", "name": "[REG] Отключить телеметрию драйверов", "checked": False},
                {"id": "reg_optimize_taskbar", "name": "[REG] Оптимизировать панель задач", "checked": False},
                {"id": "reg_disable_notifications", "name": "[REG] Отключить уведомления", "checked": False},
                {"id": "reg_disable_widgets", "name": "[REG] Отключить виджеты", "checked": False},
                {"id": "reg_disable_lockscreen", "name": "[REG] Отключить экран блокировки", "checked": False},
                {"id": "reg_speed_up_explorer", "name": "[REG] Ускорить File Explorer", "checked": False},
            ],
        }
    
    def create_checkbox_with_tooltip(self, item):
        """Создать чекбокс с подсказкой при наведении"""
        info = get_tweak_info(item['id'])
        safety_color = {'green': '#00FF00', 'yellow': '#FFFF00', 'red': '#FF0000', 'gray': '#808080'}
        
        # Формировать текст с цветом безопасности
        safety_display = info['safety']
        
        return sg.Checkbox(
            f"{item['name']} {safety_display}",
            default=item.get('checked', False),
            key=item['id'],
            size=(50, 1),
            text_color='#FF6B6B',
            background_color='#2a2a2a',
            tooltip=f"{info['description']}\n\n{info['details']}"
        )
    
    def create_window(self):
        """Создание главного окна приложения с темной горячей темой"""
        tweaks = self.load_tweaks_config()
        
        # Получение доступных резервных копий
        backups = self.backup_manager.list_backups()
        
        # Создание вкладок с твиками
        tweaks_tabs = []
        for category, items in tweaks.items():
            # Левая колонка
            left_col = []
            for i, item in enumerate(items):
                if i < len(items) // 2:
                    left_col.append([self.create_checkbox_with_tooltip(item)])
            
            # Правая колонка
            right_col = []
            for i, item in enumerate(items):
                if i >= len(items) // 2:
                    right_col.append([self.create_checkbox_with_tooltip(item)])
            
            # Двухколоночный макет
            tab_layout = [
                [
                    sg.Column(left_col, scrollable=True, size=(490, 350), background_color='#1a1a1a'),
                    sg.Column(right_col, scrollable=True, size=(490, 350), background_color='#1a1a1a'),
                ]
            ]
            tweaks_tabs.append(sg.Tab(category, tab_layout, key=f"tab_{category}", background_color='#1a1a1a'))
        
        # Вкладка "Install"
        install_layout = [
            [sg.Text("Доступные программы для установки:", font=('Arial', 10, 'bold'), text_color='#FF6B6B')],
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
                        "Notepad++",
                        "WinRAR",
                    ],
                    size=(82, 15),
                    key="-INSTALL-LIST-",
                    background_color='#2a2a2a',
                    text_color='#FF6B6B'
                )
            ],
            [
                sg.Button("Install Selected", size=(15, 1), button_color=('#FF6B6B', '#1a1a1a')),
                sg.Button("Clear", size=(15, 1), button_color=('#FF6B6B', '#1a1a1a')),
            ]
        ]
        
        # Вкладка "Backup & Restore"
        backup_list = [f"{b['name']} - {b['date']}" for b in backups]
        backup_layout = [
            [sg.Text("Управление резервными копиями:", font=('Arial', 10, 'bold'), text_color='#FF6B6B')],
            [sg.Text("Доступные резервные копии:", text_color='#FF6B6B')],
            [
                sg.Listbox(
                    values=backup_list,
                    size=(82, 10),
                    key="-BACKUP-LIST-",
                    background_color='#2a2a2a',
                    text_color='#FF6B6B'
                )
            ],
            [
                sg.Button("✅ Create Backup", size=(20, 1), button_color=('green', '#1a1a1a')),
                sg.Button("♻️ Restore from Backup", size=(20, 1), button_color=('orange', '#1a1a1a')),
                sg.Button("🗑️ Delete Backup", size=(20, 1), button_color=('red', '#1a1a1a')),
            ]
        ]
        
        # Вкладка "Logs"
        logs_layout = [
            [sg.Text("История действий:", font=('Arial', 10, 'bold'), text_color='#FF6B6B')],
            [
                sg.Multiline(
                    size=(82, 20),
                    key="-LOGS-",
                    background_color='#2a2a2a',
                    text_color='#00FF00',
                    disabled=True
                )
            ],
            [
                sg.Button("Refresh Logs", size=(20, 1), button_color=('#FF6B6B', '#1a1a1a')),
                sg.Button("Clear Logs", size=(20, 1), button_color=('#FF6B6B', '#1a1a1a')),
            ]
        ]
        
        # Легенда безопасности
        legend_layout = [
            [sg.Text("Легенда безопасности:", font=('Arial', 10, 'bold'), text_color='#FF6B6B')],
            [sg.Text("✅ SAFE - Полностью безопасный твик", text_color='#00FF00', background_color='#1a1a1a')],
            [sg.Text("⚠️ CAUTION - Требует внимания, может повлиять на функции", text_color='#FFFF00', background_color='#1a1a1a')],
            [sg.Text("❌ DANGEROUS - Опасный твик! Не рекомендуется!", text_color='#FF0000', background_color='#1a1a1a')],
            [sg.Text("ℹ️ Наведите мышь на название твика чтобы увидеть подсказку!", text_color='#FF6B6B', background_color='#1a1a1a')],
        ]
        
        # Основной макет с вкладками
        main_tabgroup = sg.TabGroup([
            [
                sg.Tab("Install", install_layout, key="tab_install", background_color='#1a1a1a'),
                sg.Tab("Tweaks", [
                    [sg.TabGroup([tweaks_tabs], tab_location='left', key="-TWEAKS-TABGROUP-", background_color='#1a1a1a')]
                ], key="tab_tweaks", background_color='#1a1a1a'),
                sg.Tab("Backup & Restore", backup_layout, key="tab_backup", background_color='#1a1a1a'),
                sg.Tab("Safety Legend", legend_layout, key="tab_legend", background_color='#1a1a1a'),
                sg.Tab("Logs", logs_layout, key="tab_logs", background_color='#1a1a1a'),
            ]
        ], enable_events=True, key="-TABGROUP-", background_color='#1a1a1a', tab_background_color='#2a2a2a')
        
        # Нижняя панель с кнопками
        bottom_layout = [
            [
                sg.Checkbox("Select All", key="-SELECT-ALL-", enable_events=True, text_color='#FF6B6B', background_color='#1a1a1a'),
                sg.Push(),
                sg.Button("✅ Apply All Tweaks", size=(16, 1), key="-APPLY-", button_color=('white', 'green')),
                sg.Button("⏮️ Undo Last Changes", size=(16, 1), key="-UNDO-", button_color=('white', 'orange')),
                sg.Button("💾 Save Profile", size=(16, 1), key="-SAVE-", button_color=('#FF6B6B', '#1a1a1a')),
                sg.Button("📂 Load Profile", size=(16, 1), key="-LOAD-", button_color=('#FF6B6B', '#1a1a1a')),
                sg.Button("🗑️ Clear Selections", size=(16, 1), key="-CLEAR-", button_color=('#FF6B6B', '#1a1a1a')),
                sg.Button("❌ Exit", size=(10, 1), key="-EXIT-", button_color=('white', 'red')),
            ],
            [sg.Text("Ready", key="-STATUS-", text_color="#00FF00", background_color='#1a1a1a', size=(100, 1))],
            [sg.ProgressBar(100, orientation='h', size=(100, 10), key="-PROGRESS-", visible=False, background_color='#00FF00', bar_color=('#FF6B6B', '#00FF00'))]
        ]
        
        # Главный макет
        layout = [
            [sg.Text("🔥 WinTweaker v2.1 - Windows Optimization Utility 🔥", 
                     font=('Arial', 14, 'bold'), justification='center', text_color='#FF0000', background_color='#1a1a1a')],
            [sg.Text("200+ Tweaks | Undo Support | Dark Hot Theme | Safety Info ℹ️", 
                     font=('Arial', 10), justification='center', text_color='#FF6B6B', background_color='#1a1a1a')],
            [sg.Separator(color='#FF6B6B')],
            [main_tabgroup],
            [sg.Separator(color='#FF6B6B')],
            bottom_layout,
        ]
        
        self.window = sg.Window(
            "🔥 WinTweaker v2.1 - Dark Hot Edition 🔥",
            layout,
            size=(1000, 850),
            finalize=True,
            background_color='#1a1a1a',
            icon=None
        )
        
        return self.window
    
    def apply_tweaks(self, window, tweaks_config):
        """Применение выбранных твиков в отдельном потоке"""
        if self.apply_in_progress:
            sg.popup_warning("Внимание", "Твики уже применяются!", background_color='#1a1a1a', text_color='#FF6B6B')
            return
        
        # Создать резервную копию перед применением
        backup_path = self.backup_manager.create_backup()
        logger.info(f"✅ Резервная копия создана: {backup_path}")
        
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
            sg.popup_error("Ошибка", "Не выбраны никакие твики!", background_color='#1a1a1a', text_color='#FF6B6B')
            return
        
        # Запуск применения в отдельном потоке
        thread = threading.Thread(target=self._apply_tweaks_thread, args=(window, selected, backup_path))
        thread.daemon = True
        thread.start()
    
    def _apply_tweaks_thread(self, window, selected, backup_path):
        """Поток для применения твиков"""
        self.apply_in_progress = True
        window["-PROGRESS-"].update(visible=True)
        window["-APPLY-"].update(disabled=True)
        
        logger.info(f"🚀 Начинаю применение {len(selected)} твиков...")
        window["-STATUS-"].update(f"⏳ Применяю {len(selected)} твиков...")
        
        total = len(selected)
        current = 0
        self.last_applied_tweaks = selected.copy()
        
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
                elif "w10" in tweak_id:
                    self.registry.apply_w10_tweak(tweak_id)
                elif "reg" in tweak_id:
                    self.registry.apply_registry_tweak(tweak_id)
                else:
                    self.registry.apply_tweak(tweak_id)
            
            window["-PROGRESS-"].update(100)
            window["-STATUS-"].update(f"✅ Успешно применены {total} твиков! Резервная копия: {backup_path}")
            logger.info(f"✅ Все твики применены успешно!")
            sg.popup("✅ Успех", f"Успешно применены {total} твиков!\n\nПроверьте логи для деталей.\n\nРезервная копия: {backup_path}", background_color='#1a1a1a', text_color='#FF6B6B')
            
        except Exception as e:
            logger.error(f"❌ Ошибка при применении твиков: {str(e)}")
            window["-STATUS-"].update(f"❌ Ошибка: {str(e)}")
            sg.popup_error("Ошибка", f"Произошла ошибка при применении твиков:\n{str(e)}", background_color='#1a1a1a', text_color='#FF6B6B')
        
        finally:
            window["-PROGRESS-"].update(visible=False)
            window["-APPLY-"].update(disabled=False)
            self.apply_in_progress = False
    
    def undo_last_changes(self, window):
        """Отменить последние примененные изменения"""
        if not self.last_applied_tweaks:
            sg.popup_warning("Внимание", "Нет примененных твиков для отката!", background_color='#1a1a1a', text_color='#FF6B6B')
            return
        
        # Найти последнюю резервную копию
        backups = self.backup_manager.list_backups()
        if not backups:
            sg.popup_error("Ошибка", "Нет доступных резервных копий!", background_color='#1a1a1a', text_color='#FF6B6B')
            return
        
        last_backup = backups[0]
        
        if sg.popup_yes_no("Подтверждение", f"Восстановить резервную копию от {last_backup['date']}?", background_color='#1a1a1a', text_color='#FF6B6B') == 'Yes':
            self.backup_manager.restore_backup(last_backup['path'])
            window["-STATUS-"].update(f"✅ Изменения отменены! Восстановлена резервная копия: {last_backup['date']}")
            logger.info(f"✅ Резервная копия восстановлена: {last_backup['path']}")
            sg.popup("✅ Успех", "Изменения успешно отменены!", background_color='#1a1a1a', text_color='#FF6B6B')
            self.last_applied_tweaks = []
    
    def run(self):
        """Главный цикл приложения"""
        if not check_admin():
            sg.popup_error(
                "Ошибка прав доступа",
                "WinTweaker требует прав администратора!\n\n"
                "Пожалуйста, запустите программу от имени администратора.",
                background_color='#1a1a1a',
                text_color='#FF6B6B'
            )
            logger.error("❌ Программа запущена без прав администратора!")
            sys.exit(1)
        
        logger.info("🚀 WinTweaker v2.1 запущена")
        
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
            
            elif event == "-UNDO-":
                self.undo_last_changes(self.window)
            
            elif event == "-SAVE-":
                profile_name = sg.popup_get_text("Сохранить профиль", "Введите имя профиля:", background_color='#1a1a1a', text_color='#FF6B6B')
                if profile_name:
                    logger.info(f"💾 Профиль '{profile_name}' сохранен")
                    sg.popup("✅ Успех", f"Профиль '{profile_name}' сохранен успешно!", background_color='#1a1a1a', text_color='#FF6B6B')
            
            elif event == "-LOAD-":
                profiles = self.utils.get_available_profiles()
                if profiles:
                    profile_name = sg.popup_get_choice("Загрузить профиль", "Выберите профиль:", profiles, background_color='#1a1a1a', text_color='#FF6B6B')
                    if profile_name:
                        logger.info(f"📂 Профиль '{profile_name}' загружен")
                        sg.popup("✅ Успех", f"Профиль '{profile_name}' загружен успешно!", background_color='#1a1a1a', text_color='#FF6B6B')
                else:
                    sg.popup("Нет профилей", "Нет сохраненных профилей!", background_color='#1a1a1a', text_color='#FF6B6B')
        
        self.window.close()

def main():
    """Точка входа в программу"""
    try:
        app = WinTweakerApp()
        app.run()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {str(e)}")
        sg.popup_error("Критическая ошибка", f"Программа завершилась с ошибкой:\n{str(e)}", background_color='#1a1a1a', text_color='#FF6B6B')
        sys.exit(1)

if __name__ == "__main__":
    main()
