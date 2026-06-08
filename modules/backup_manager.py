"""
Backup Manager - Управление резервными копиями реестра
"""

import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class BackupManager:
    """Класс для управления резервными копиями"""
    
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        self.backup_index_file = os.path.join(self.backup_dir, "backup_index.json")
    
    def create_backup(self):
        """Создать резервную копию реестра"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"registry_backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.reg")
            
            # Экспортировать реестр
            subprocess.run(
                ["reg", "export", "HKLM", backup_path],
                capture_output=True,
                timeout=60
            )
            
            # Сохранить информацию о резервной копии
            backup_info = {
                "name": backup_name,
                "path": backup_path,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
            }
            
            self._save_backup_info(backup_info)
            logger.info(f"✅ Резервная копия создана: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка при создании резервной копии: {str(e)}")
            return None
    
    def restore_backup(self, backup_path):
        """Восстановить резервную копию реестра"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"❌ Резервная копия не найдена: {backup_path}")
                return False
            
            # Импортировать реестр
            subprocess.run(
                ["reg", "import", backup_path],
                capture_output=True,
                timeout=60
            )
            
            logger.info(f"✅ Резервная копия восстановлена: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при восстановлении резервной копии: {str(e)}")
            return False
    
    def list_backups(self):
        """Получить список всех резервных копий"""
        try:
            if not os.path.exists(self.backup_index_file):
                return []
            
            with open(self.backup_index_file, 'r', encoding='utf-8') as f:
                backups = json.load(f)
            
            # Сортировать по дате (новые в начале)
            backups.sort(key=lambda x: x['date'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка резервных копий: {str(e)}")
            return []
    
    def delete_backup(self, backup_path):
        """Удалить резервную копию"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"✅ Резервная копия удалена: {backup_path}")
                
                # Обновить индекс
                backups = self.list_backups()
                backups = [b for b in backups if b['path'] != backup_path]
                self._save_all_backups_info(backups)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении резервной копии: {str(e)}")
            return False
    
    def _save_backup_info(self, backup_info):
        """Сохранить информацию о новой резервной копии"""
        try:
            backups = self.list_backups()
            backups.insert(0, backup_info)
            
            # Хранить только последние 20 резервных копий
            backups = backups[:20]
            
            self._save_all_backups_info(backups)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении информации о резервной копии: {str(e)}")
    
    def _save_all_backups_info(self, backups):
        """Сохранить информацию о всех резервных копиях"""
        try:
            with open(self.backup_index_file, 'w', encoding='utf-8') as f:
                json.dump(backups, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении индекса резервных копий: {str(e)}")
    
    def cleanup_old_backups(self, max_backups=20):
        """Удалить старые резервные копии"""
        try:
            backups = self.list_backups()
            
            if len(backups) > max_backups:
                for backup in backups[max_backups:]:
                    self.delete_backup(backup['path'])
            
            logger.info(f"✅ Старые резервные копии удалены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке старых резервных копий: {str(e)}")
