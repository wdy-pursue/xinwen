import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 自动查找config.ini文件
            # 首先尝试当前目录
            if os.path.exists("config.ini"):
                config_path = "config.ini"
            else:
                # 如果当前目录没有，尝试父目录（适用于src目录中运行的情况）
                parent_config = os.path.join("..", "config.ini")
                if os.path.exists(parent_config):
                    config_path = parent_config
                else:
                    # 如果父目录也没有，尝试项目根目录
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    root_config = os.path.join(project_root, "config.ini")
                    if os.path.exists(root_config):
                        config_path = root_config
                    else:
                        config_path = "config.ini"  # 默认回退
        
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self._config is None:
            try:
                logger.info(f"尝试加载配置文件: {os.path.abspath(self.config_path)}")
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info("配置文件加载成功")
            except FileNotFoundError:
                logger.error(f"配置文件未找到: {os.path.abspath(self.config_path)}")
                logger.error("请确保config.ini文件在项目根目录中")
                self._config = {}
            except json.JSONDecodeError as e:
                logger.error(f"配置文件格式错误: {e}")
                self._config = {}
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self._config = {}
        return self._config
    
    def get(self, key: str, default=None):
        """获取配置项"""
        config = self.load_config()
        return config.get(key, default)
    
    def get_nested(self, *keys, default=None):
        """获取嵌套配置项"""
        config = self.load_config()
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        return config