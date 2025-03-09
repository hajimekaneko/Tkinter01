import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def write_json_output(data: dict) -> str:
    """
    data の内容を OUTPUT フォルダに JSON ファイルとして保存し、
    作成したファイルパスを返す関数
    """
    output_folder = "././Out"
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except Exception as e:
            logger.error("OUTPUTフォルダの作成に失敗: %s", e)
    filename = os.path.join(output_folder, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error("JSONファイル書き出しエラー: %s", e)
    return filename
