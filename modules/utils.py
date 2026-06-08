"""
Utilities module - вспомогательные функции
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Utils:
    """Класс для вспомогательных функций"""
    
    @staticmethod
    def create_backup():
        """Создать резервную копию реестра"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"registry_backup_{timestamp}.reg")
            
            logger.info(f"💾 Создание резервной копии реестра: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"❌ Ошибка при создании резервной копии: {str(e)}")
            return None
    
    @staticmethod
    def save_profile(profile_name, tweaks_state):
        """Сохранить профиль твиков"""
        try:
            profiles_dir = "config/profiles"
            os.makedirs(profiles_dir, exist_ok=True)
            
            profile_file = os.path.join(profiles_dir, f"{profile_name}.json")
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(tweaks_state, f, indent=4, ensure_ascii=False)
            
            logger.info(f"💾 Профиль '{profile_name}' сохранен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении профиля: {str(e)}")
            return False
    
    @staticmethod
    def load_profile(profile_name):
        """Загрузить профиль твиков"""
        try:
            profile_file = os.path.join("config/profiles", f"{profile_name}.json")
            
            if not os.path.exists(profile_file):
                logger.warning(f"⚠️ Профиль '{profile_name}' не найден")
                return None
            
            with open(profile_file, 'r', encoding='utf-8') as f:
                tweaks_state = json.load(f)
            
            logger.info(f"📂 Профиль '{profile_name}' загружен")
            return tweaks_state
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке профиля: {str(e)}")
            return None
    
    @staticmethod
    def get_available_profiles():
        """Получить список доступных профилей"""
        try:
            profiles_dir = "config/profiles"
            if not os.path.exists(profiles_dir):
                return []
            
            profiles = []
            for filename in os.listdir(profiles_dir):
                if filename.endswith('.json'):
                    profiles.append(filename[:-5])
            
            return profiles
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка профилей: {str(e)}")
            return []
    
    @staticmethod
    def format_file_size(size_bytes):
        """Форматировать размер файла в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
