import os
import shutil
import logging

logger = logging.getLogger(__name__)

def clear_folder_contents(folder_path: str):
    """
    指定されたフォルダ (folder_path) 内のすべてのファイル・ディレクトリを削除し、
    フォルダ自体はそのまま残す共通関数。
    """
    if not os.path.exists(folder_path):
        return
    try:
        for entry in os.scandir(folder_path):
            path = entry.path
            if entry.is_file() or entry.is_symlink():
                os.remove(path)
            elif entry.is_dir():
                shutil.rmtree(path)
        logger.info("フォルダ内の全ファイル・ディレクトリを削除しました: %s", folder_path)
    except Exception as e:
        logger.error("フォルダ内の削除に失敗しました (%s): %s", folder_path, e)
