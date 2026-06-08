"""
Services manager module - управление сервисами Windows
"""

import subprocess
import logging

logger = logging.getLogger(__name__)

class ServiceManager:
    """Класс для управления сервисами Windows"""
    
    def __init__(self):
        self.background_services = [
            "DiagTrack",
            "dmwappushservice",
            "OneSyncSvc",
            "WSearch",
            "XblAuthManager",
            "XblGameSave",
            "XboxNetApiSvc",
            "XboxGipSvc",
        ]
    
    def disable_service(self, service_name):
        """Отключить сервис"""
        try:
            subprocess.run(
                ["net", "stop", service_name],
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["sc", "config", service_name, "start=disabled"],
                capture_output=True,
                timeout=10
            )
            logger.info(f"✅ Сервис '{service_name}' отключен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при отключении сервиса '{service_name}': {str(e)}")
            return False
    
    def disable_background_apps(self):
        """Отключить фоновые приложения"""
        for service in self.background_services:
            self.disable_service(service)
        logger.info("✅ Фоновые приложения отключены")
    
    def enable_service(self, service_name):
        """Включить сервис"""
        try:
            subprocess.run(
                ["sc", "config", service_name, "start=auto"],
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["net", "start", service_name],
                capture_output=True,
                timeout=10
            )
            logger.info(f"✅ Сервис '{service_name}' включен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при включении сервиса '{service_name}': {str(e)}")
            return False
