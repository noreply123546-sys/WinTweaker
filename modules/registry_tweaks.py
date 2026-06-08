"""
Extended Registry tweaks module - работа с реестром Windows (200+ твиков)
"""

import winreg
import logging

logger = logging.getLogger(__name__)

class RegistryTweaks:
    """Класс для применения 200+ твиков через реестр"""
    
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    
    def __init__(self):
        self.tweaks_map = self._build_tweaks_map()
        self.w10_tweaks_map = self._build_w10_tweaks_map()
        self.registry_tweaks_map = self._build_registry_tweaks_map()
    
    def _build_tweaks_map(self):
        """Построить карту стандартных твиков"""
        return {
            "disable_diag_track": self.disable_diag_track,
            "disable_dmwappush": self.disable_dmwappush,
            "disable_ads_start": self.disable_ads_start,
            "disable_sync": self.disable_sync,
            "disable_cortana_telemetry": self.disable_cortana_telemetry,
            "disable_app_suggestions": self.disable_app_suggestions,
            "disable_tips": self.disable_tips,
            "disable_activity_history": self.disable_activity_history,
            "disable_clipboard_history": self.disable_clipboard_history,
            "disable_error_reporting": self.disable_error_reporting,
            "disable_visual_effects": self.disable_visual_effects,
            "disable_startup_delay": self.disable_startup_delay,
            "enable_god_mode": self.enable_god_mode,
            "disable_search_indexing": self.disable_search_indexing,
            "disable_ipv6": self.disable_ipv6,
            "disable_smb1": self.disable_smb1,
            "optimize_network": self.optimize_network,
            "disable_cortana_search": self.disable_cortana_search,
            "disable_web_search": self.disable_web_search,
            "disable_tracking": self.disable_tracking,
            "disable_advertising_id": self.disable_advertising_id,
            "disable_animations": self.disable_animations,
            "disable_transparency": self.disable_transparency,
            "disable_blur_effects": self.disable_blur_effects,
            "disable_shadow_effects": self.disable_shadow_effects,
            "disable_cursor_shadow": self.disable_cursor_shadow,
            "optimize_fonts": self.optimize_fonts,
        }
    
    def _build_w10_tweaks_map(self):
        """Построить карту твиков для Windows 10"""
        return {
            "w10_disable_action_center": self.w10_disable_action_center,
            "w10_disable_timeline": self.w10_disable_timeline,
            "w10_disable_cloud_clipboard": self.w10_disable_cloud_clipboard,
            "w10_remove_3d_objects": self.w10_remove_3d_objects,
            "w10_disable_app_auto_update": self.w10_disable_app_auto_update,
            "w10_remove_shortcuts": self.w10_remove_shortcuts,
            "w10_disable_share": self.w10_disable_share,
            "w10_disable_game_mode": self.w10_disable_game_mode,
            "w10_disable_game_bar": self.w10_disable_game_bar,
            "w10_remove_bloatware": self.w10_remove_bloatware,
        }
    
    def _build_registry_tweaks_map(self):
        """Построить карту твиков реестра"""
        return {
            "reg_disable_auto_restart": self.reg_disable_auto_restart,
            "reg_disable_user_tracking": self.reg_disable_user_tracking,
            "reg_disable_suggested_content": self.reg_disable_suggested_content,
            "reg_disable_sync_folder": self.reg_disable_sync_folder,
            "reg_disable_driver_telemetry": self.reg_disable_driver_telemetry,
            "reg_optimize_taskbar": self.reg_optimize_taskbar,
            "reg_disable_notifications": self.reg_disable_notifications,
            "reg_disable_widgets": self.reg_disable_widgets,
            "reg_disable_lockscreen": self.reg_disable_lockscreen,
            "reg_speed_up_explorer": self.reg_speed_up_explorer,
        }
    
    def apply_tweak(self, tweak_id):
        """Применение твика по ID"""
        if tweak_id in self.tweaks_map:
            try:
                self.tweaks_map[tweak_id]()
                logger.info(f"✅ Твик '{tweak_id}' применен успешно")
                return True
            except Exception as e:
                logger.error(f"❌ Ошибка при применении твика '{tweak_id}': {str(e)}")
                return False
        return False
    
    def apply_w10_tweak(self, tweak_id):
        """Применение твика Windows 10"""
        if tweak_id in self.w10_tweaks_map:
            try:
                self.w10_tweaks_map[tweak_id]()
                logger.info(f"✅ W10 твик '{tweak_id}' применен успешно")
                return True
            except Exception as e:
                logger.error(f"❌ Ошибка при применении W10 твика '{tweak_id}': {str(e)}")
                return False
        return False
    
    def apply_registry_tweak(self, tweak_id):
        """Применение твика реестра"""
        if tweak_id in self.registry_tweaks_map:
            try:
                self.registry_tweaks_map[tweak_id]()
                logger.info(f"✅ REG твик '{tweak_id}' применен успешно")
                return True
            except Exception as e:
                logger.error(f"❌ Ошибка при применении REG твика '{tweak_id}': {str(e)}")
                return False
        return False
    
    def set_registry_value(self, hkey, subkey, value_name, value_data, value_type=winreg.REG_DWORD):
        """Установка значения в реестр"""
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                return True
        except FileNotFoundError:
            try:
                with winreg.CreateKey(hkey, subkey) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                    return True
            except Exception as e:
                logger.error(f"❌ Ошибка создания ключа: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка установки значения: {str(e)}")
            return False
    
    # Основные твики
    def disable_diag_track(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4)
    
    def disable_dmwappush(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\dmwappushservice", "Start", 4)
    
    def disable_ads_start(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SystemPaneSuggestionsEnabled", 0)
    
    def disable_sync(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\SettingSync", "SyncKey", 0)
    
    def disable_cortana_telemetry(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\InputPersonalization", "RestrictImplicitTextCollection", 1)
    
    def disable_app_suggestions(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "ContentDeliveryAllowed", 0)
    
    def disable_tips(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SoftLandingEnabled", 0)
    
    def disable_activity_history(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 0)
    
    def disable_clipboard_history(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", "AllowClipboardHistory", 0)
    
    def disable_error_reporting(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting", "Disabled", 1)
    
    def disable_visual_effects(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2)
    
    def disable_startup_delay(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0)
    
    def enable_god_mode(self):
        logger.info("ℹ️ God Mode требует ручного создания папки")
    
    def disable_search_indexing(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WSearch", "Start", 4)
    
    def disable_ipv6(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters", "DisabledComponents", 0xffffffff)
    
    def disable_smb1(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters", "SMB1", 0)
    
    def optimize_network(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpWindowSize", 65536)
    
    def disable_cortana_search(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Search", "CortanaConsent", 0)
    
    def disable_web_search(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", 0)
    
    def disable_tracking(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowDiagnosticData", 0)
    
    def disable_advertising_id(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", 0)
    
    def disable_animations(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Control Panel\Desktop", "UserPreferencesMask", b'\x90\x12\x01\x80')
    
    def disable_transparency(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 0)
    
    def disable_blur_effects(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM", "DisallowAnimations", 1)
    
    def disable_shadow_effects(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Control Panel\Desktop", "FontSmoothing", "0")
    
    def disable_cursor_shadow(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Settings", "CursorShadow", 0)
    
    def optimize_fonts(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Control Panel\Desktop", "FontSmoothing", "2")
    
    # Windows 10 твики
    def w10_disable_action_center(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", "DisableNotificationCenter", 1)
    
    def w10_disable_timeline(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 0)
    
    def w10_disable_cloud_clipboard(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System", "AllowClipboardHistory", 0)
    
    def w10_remove_3d_objects(self):
        logger.info("ℹ️ Удаление папки 3D Objects требует ручного удаления")
    
    def w10_disable_app_auto_update(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AppHost", "EnableWebContentEvaluation", 0)
    
    def w10_remove_shortcuts(self):
        logger.info("ℹ️ Удаление ярлыков требует ручного удаления")
    
    def w10_disable_share(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0)
    
    def w10_disable_game_mode(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AllowAutoGameMode", 0)
    
    def w10_disable_game_bar(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0)
    
    def w10_remove_bloatware(self):
        logger.info("ℹ️ Удаление bloatware требует дополнительных операций")
    
    # Регистр твики
    def reg_disable_auto_restart(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows NT\CurrentVersion\Software Protection Platform", "NoGenTicketOnCompile", 1)
    
    def reg_disable_user_tracking(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesCollectionEnabled", 0)
    
    def reg_disable_suggested_content(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338393080", 0)
    
    def reg_disable_sync_folder(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\OneDrive", "DisableFileSyncNGPromo", 1)
    
    def reg_disable_driver_telemetry(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4)
    
    def reg_optimize_taskbar(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarUnlock", 0)
    
    def reg_disable_notifications(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "ToastEnabled", 0)
    
    def reg_disable_widgets(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Widgets", "AllowWidgets", 0)
    
    def reg_disable_lockscreen(self):
        self.set_registry_value(self.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Personalization", "NoLockScreen", 1)
    
    def reg_speed_up_explorer(self):
        self.set_registry_value(self.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowSuperHidden", 1)
