import json
import os
from datetime import datetime
import logging
from config import TMP_FOLDER
from infrastructure.utils import ensure_folder_exists

logger = logging.getLogger(__name__)

def write_json_output(data: dict, out_filename: str = None) -> str:
    """
    data の内容を TMP_FOLDER に JSON ファイルとして保存し、
    作成したファイルパスを返す関数。
    out_filename が指定されなければ "output_YYYYMMDD_HHMMSS.json" を生成します。
    """
    ensure_folder_exists(TMP_FOLDER)
    if not out_filename:
        out_filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = os.path.join(TMP_FOLDER, out_filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error("JSONファイル書き出しエラー: %s", e)
    return file_path
