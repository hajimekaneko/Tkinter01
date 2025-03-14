import json
import os
import logging
from config import TMP_FOLDER, OUT_FOLDER
from infrastructure.utils import ensure_folder_exists

logger = logging.getLogger(__name__)

def merge_json_files_by_unit(keywords: list) -> dict:
    """
    TMP_FOLDER 内の JSON ファイルを、ファイル名に含まれる単位（keywords に該当する文字列）ごとに合算する。
    
    合算処理:
      - 各 JSON ファイルは XLSX 変換時の出力（構造は { sheet: { group: [row, ...], ... }, ... } ）とする。
      - 各 row について、結合主キー「グループ」「指図書No」「補足」でマージし、時間の値を合計する。
      - 合算対象の行（時間が数値の場合）は、"merged_files" フィールドに寄与したファイル名を必ずリストで追加する。
    出力は unit ごとに OUT_FOLDER に output_{unit}.json として保存し、
    戻り値は unit → 出力ファイルパス の辞書です。
    """
    merged_data = {}
    ensure_folder_exists(OUT_FOLDER)
    for filename in os.listdir(TMP_FOLDER):
        if not filename.lower().endswith(".json"):
            continue
        file_path = os.path.join(TMP_FOLDER, filename)
        unit_found = None
        for kw in keywords:
            if kw in filename:
                unit_found = kw
                break
        if not unit_found:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("JSON読み込みエラー %s: %s", file_path, e)
            continue
        if unit_found not in merged_data:
            merged_data[unit_found] = {}
        for sheet, groups in data.items():
            for group, rows in groups.items():
                for row in rows:
                    try:
                        key = (
                            str(row["グループ"]).strip(),
                            str(row["指図書No"]).strip(),
                            str(row["補足"]).strip()
                        )
                    except Exception as e:
                        logger.error("必要なキーが存在しない行: %s", row)
                        continue
                    try:
                        time_val = float(row["時間"])
                    except Exception as e:
                        logger.error("時間の値が不正な行 (ファイル %s): %s", file_path, row)
                        continue
                    if key in merged_data[unit_found]:
                        merged_entry = merged_data[unit_found][key]
                        merged_entry["時間"] += time_val
                        if "merged_files" in merged_entry:
                            if filename not in merged_entry["merged_files"]:
                                merged_entry["merged_files"].append(filename)
                        else:
                            merged_entry["merged_files"] = [filename]
                    else:
                        new_row = row.copy()
                        new_row["時間"] = time_val
                        new_row["merged_files"] = [filename]
                        merged_data[unit_found][key] = new_row
    output_paths = {}
    for unit, rows_dict in merged_data.items():
        merged_list = list(rows_dict.values())
        out_filename = f"output_{unit}.json"
        out_path = os.path.join(OUT_FOLDER, out_filename)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(merged_list, f, ensure_ascii=False, indent=4)
            output_paths[unit] = out_path
        except Exception as e:
            logger.error("出力ファイル書き出しエラー (%s): %s", out_path, e)
    return output_paths
