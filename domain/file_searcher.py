import os
import logging

logger = logging.getLogger(__name__)

def search_files(folder_path: str, keywords: list, current_depth: int = 0, max_depth: int = 3, base_folder: str = None) -> list:
    """
    指定フォルダおよびサブディレクトリ（最大階層まで）から、
    キーワードに部分一致するファイルの相対パスを取得する関数
    """
    if base_folder is None:
        base_folder = folder_path
    matched_files = []
    if current_depth > max_depth:
        return matched_files
    try:
        for entry in os.listdir(folder_path):
            full_path = os.path.join(folder_path, entry)
            if os.path.isfile(full_path):
                if any(keyword in entry for keyword in keywords):
                    matched_files.append(os.path.relpath(full_path, base_folder))
            elif os.path.isdir(full_path):
                matched_files.extend(
                    search_files(full_path, keywords, current_depth + 1, max_depth, base_folder)
                )
    except Exception as e:
        logger.error("探索中のエラー: %s", e)
    return matched_files
