import os

def ensure_folder_exists(folder_path: str):
    """フォルダが存在しなければ作成する"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)