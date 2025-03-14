import json
import os
import logging

logger = logging.getLogger(__name__)

def merge_json_files_by_unit(keywords: list) -> dict:
    """
    Tmp フォルダ内にある JSON ファイルを、ファイル名に含まれる単位（keywords に該当する文字列）ごとに合算する。
    
    合算処理:
      - 各 JSON ファイルは、XLSX 変換時の出力と想定し、構造は { sheet: { group: [row, ...], ... }, ... } とする。
      - 各 row に対し、キーとして「グループ」「指図書No」「補足」を結合主キーとし、
        「時間」フィールドの数値を合計します。
      - なお、時間が null 以外でマージ対象となった場合、その行に対して、合算に寄与したファイル名を
        "merged_files" というフィールドにリストで追加します。
    出力は unit ごとにリスト（各行は辞書）となり、OUT フォルダに
      output_{unit}.json というファイル名で保存されます。
    戻り値は、unit → 出力ファイルパス の辞書です。
    """
    merged_data = {}  # unit -> { composite_key: row }
    
    # プロジェクトルートの取得 (このファイルから 2階層上)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..")
    tmp_folder = os.path.join(project_root, "Tmp")
    out_folder = os.path.join(project_root, "OUT")
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
    # Tmp フォルダ内の JSON ファイルをリスト
    for filename in os.listdir(tmp_folder):
        if not filename.lower().endswith(".json"):
            continue
        file_path = os.path.join(tmp_folder, filename)
        # unit を決定： keywords のいずれかがファイル名に含まれていればその単位とする
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
        
        # 初回は unit_found をキーに初期化
        if unit_found not in merged_data:
            merged_data[unit_found] = {}
        
        # data は { sheet: { group: [row, ...], ... }, ... }
        for sheet, groups in data.items():
            for group, rows in groups.items():
                for row in rows:
                    try:
                        # 結合主キー：「グループ」「指図書No」「補足」
                        key = (
                            str(row["グループ"]).strip(),
                            str(row["指図書No"]).strip(),
                            str(row["補足"]).strip()
                        )
                    except Exception as e:
                        logger.error("必要なキーが存在しない行: %s", row)
                        continue
                    # 時間がnull以外なら数値変換
                    try:
                        time_val = float(row["時間"])
                    except Exception as e:
                        logger.error("時間の値が不正な行 (ファイル %s): %s", file_path, row)
                        continue
                    # マージ対象の行には、merged_files フィールドを追加する
                    if key in merged_data[unit_found]:
                        merged_entry = merged_data[unit_found][key]
                        merged_entry["時間"] += time_val
                        # すでにこのファイル名が登録されていなければ追加
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
    
    # 各 unit ごとに、merged_data[unit] をリスト化して出力
    output_paths = {}
    for unit, rows_dict in merged_data.items():
        merged_list = list(rows_dict.values())
        out_filename = f"output_{unit}.json"
        out_path = os.path.join(out_folder, out_filename)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(merged_list, f, ensure_ascii=False, indent=4)
            output_paths[unit] = out_path
        except Exception as e:
            logger.error("出力ファイル書き出しエラー (%s): %s", out_path, e)
    return output_paths
