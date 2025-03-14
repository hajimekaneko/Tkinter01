import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def write_json_output(data: dict, out_filename: str = None) -> str:
    """
    data の内容をプロジェクトルート直下の Tmp フォルダに JSON ファイルとして保存し、
    作成したファイルパスを返す関数。
    
    out_filename が指定された場合はその名前を使用し、
    指定がなければ "output_YYYYMMDD_HHMMSS.json" を生成します。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..")
    output_folder = os.path.join(project_root, "Tmp")

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except Exception as e:
            logger.error("Tmpフォルダの作成に失敗: %s", e)

    if not out_filename:
        out_filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    file_path = os.path.join(output_folder, out_filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error("JSONファイル書き出しエラー: %s", e)
    return file_path
