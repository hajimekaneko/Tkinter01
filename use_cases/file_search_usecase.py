from domain.file_searcher import search_files

def get_matched_files(folder_path: str, keywords: list) -> list:
    """
    指定フォルダから、キーワードに合致するファイル一覧（相対パス）を取得するユースケース
    """
    return search_files(folder_path, keywords)
