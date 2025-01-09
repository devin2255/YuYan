# 动态加载 models 文件夹下的所有模块
import os
from pathlib import Path


def load_models_from_folder(folder: str = './'):
    models = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = Path(root) / file
                module_name = str(module_path.with_suffix("")).replace("/", ".").replace("\\", ".")
                models.append(module_name)
    # print(models)
    return models
