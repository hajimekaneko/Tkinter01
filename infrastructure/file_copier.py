import os
import shutil
import logging

logger = logging.getLogger(__name__)

def copy_xlsx_file(in_file_path: str, base_folder: str) -> str:
    """
    INフォルダにある指定の XLSX ファイル（in_file_path）を、INフォルダからの相対パス情報を用いて
    プロジェクトルート直下の Tmp フォルダにコピーします。
    コピー先ファイル名は、相対パスの区切り文字（/ や \）をアンダースコアに置換したものとし、
    ".." などの不要な部分は取り除きます。
    コピー先のファイルパスを返します。
    """
    # プロジェクトルートの取得（現在のファイルから2階層上）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..")
    tmp_folder = os.path.join(project_root, "Tmp")
    
    if not os.path.exists(tmp_folder):
        try:
            os.makedirs(tmp_folder)
        except Exception as e:
            logger.error("Tmpフォルダの作成に失敗: %s", e)
            raise e
    
    # INフォルダからの相対パスを取得
    rel_path = os.path.relpath(in_file_path, base_folder)
    # 不要な ".." を取り除く（例えば "../" を削除）
    rel_path = rel_path.replace("..", "")
    # os.sep で区切り文字をアンダースコアに置換（Windowsの場合は "\"、Unix系は "/"）
    new_filename = rel_path.replace(os.sep, "_")
    # もし "/" や "\" が混在している場合も置換
    new_filename = new_filename.replace("/", "_").replace("\\", "_")
    
    dest_path = os.path.join(tmp_folder, new_filename)
    
    try:
        shutil.copy2(in_file_path, dest_path)
    except Exception as e:
        logger.error("XLSXファイルのコピーに失敗 (%s -> %s): %s", in_file_path, dest_path, e)
        raise e
    
    return dest_path
