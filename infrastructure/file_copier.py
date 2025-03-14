import os
import shutil
import logging
from config import TMP_FOLDER
from infrastructure.utils import ensure_folder_exists

logger = logging.getLogger(__name__)

def copy_xlsx_file(in_file_path: str, base_folder: str) -> str:
    """
    INフォルダ内の指定 XLSX ファイル（in_file_path）を、
    INフォルダからの相対パス情報を用いて TMP_FOLDER にコピーする。
    コピー先のファイル名は、相対パスの区切り文字をアンダースコアに置換し、
    不要な ".." 部分は除去して生成します。
    コピー先のファイルパスを返します。
    """
    ensure_folder_exists(TMP_FOLDER)
    rel_path = os.path.relpath(in_file_path, base_folder)
    rel_path = rel_path.replace("..", "")
    new_filename = rel_path.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
    dest_path = os.path.join(TMP_FOLDER, new_filename)
    try:
        shutil.copy2(in_file_path, dest_path)
    except Exception as e:
        logger.error("XLSXファイルのコピーに失敗 (%s -> %s): %s", in_file_path, dest_path, e)
        raise e
    return dest_path
