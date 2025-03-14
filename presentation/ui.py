import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os
from use_cases.file_search_usecase import get_matched_files
from infrastructure.json_writer import write_json_output

logger = logging.getLogger(__name__)

class FileSearchUI(tk.Frame):
    def __init__(self, root, keywords):
        super().__init__(root, width=600, height=600, borderwidth=1, relief='groove')
        self.root = root
        self.keywords = keywords  # 例: ["金子", "丸山"]
        self.base_folder = None   # ユーザーが選択したINフォルダのパス
        self.pack(fill=tk.BOTH, expand=True)
        self.pack_propagate(0)
        self.create_widgets()
    
    def create_widgets(self):
        # --- 上部：ボタン群 ---
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.select_folder_button = tk.Button(button_frame, text="フォルダを選択", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=5)
        self.info_button = tk.Button(button_frame, text="情報取得", command=self.show_selected_info)
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.merge_button = tk.Button(button_frame, text="合算処理", command=self.merge_json_files)
        self.merge_button.pack(side=tk.LEFT, padx=5)
        self.close_button = tk.Button(button_frame, text="閉じる", command=self.root.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)
        
        # --- 中央：ステータスバー ---
        self.status_label = tk.Label(self, text="次の作業: フォルダを選択してください", anchor='w', relief=tk.SUNKEN)
        self.status_label.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        # --- 下部：ファイル一覧 ---
        list_frame = tk.Frame(self)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(list_frame, text="ファイル一覧").pack(anchor='w')
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
    
    def select_folder(self):
        # プロジェクトルートと Tmp フォルダを特定し、Tmp フォルダが存在する場合は削除
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, "..", "..")
        tmp_folder = os.path.join(project_root, "Tmp")
        if os.path.exists(tmp_folder):
            try:
                shutil.rmtree(tmp_folder)
                logger.info("Tmp フォルダの内容を削除しました: %s", tmp_folder)
            except Exception as e:
                logger.error("Tmp フォルダ削除に失敗: %s", e)
        
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.base_folder = folder_path  # ユーザーが選択したINフォルダのパスを保持
            self.populate_file_list(folder_path)
            self.status_label.config(text="次の作業: XLSXファイルを選択し、情報取得ボタンをクリックしてください")
    
    def populate_file_list(self, folder_path):
        self.file_listbox.delete(0, tk.END)
        try:
            matched_files = get_matched_files(folder_path, self.keywords)
            if matched_files:
                for file in matched_files:
                    self.file_listbox.insert(tk.END, file)
            else:
                self.file_listbox.insert(tk.END, "一致するファイルがありません")
        except Exception as e:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, f"エラー: {e}")
            logger.error("ファイルリストの取得中にエラー: %s", e)
    
    def show_selected_info(self):
        """
        選択された XLSX ファイルについて、
          1. INフォルダから Tmpフォルダへ、対象ファイルをコピー(copy_xlsx_file を利用）
          2. Tmpフォルダ内のコピー先ファイルを対象に、XLSX の内容を JSON に変換する。
             出力ファイル名は、コピー先ファイル名の拡張子 .xlsx を .json に置換します。
        結果は、各元ファイルと生成された JSON ファイルのパス一覧をメッセージボックスで表示します。
        """
        try:
            selected_indices = self.file_listbox.curselection()
            files = self.file_listbox.get(0, tk.END)
            if not selected_indices:
                messagebox.showinfo("情報", "ファイルが選択されていません。")
                return
            
            json_file_paths = []
            for idx in selected_indices:
                file = files[idx]
                if file.lower().endswith(".xlsx"):
                    in_file_path = os.path.join(self.base_folder, file)
                    # コピー処理：INフォルダから Tmpフォルダへコピー
                    from infrastructure.file_copier import copy_xlsx_file
                    tmp_file_path = copy_xlsx_file(in_file_path, self.base_folder)
                    
                    # JSON出力ファイル名：元ファイルの相対パス（区切りはアンダースコア）から拡張子を .json に
                    base_name, _ = os.path.splitext(os.path.basename(tmp_file_path))
                    out_filename = f"{base_name}.json"
                    
                    # XLSX の内容を JSON 辞書として抽出
                    from infrastructure.xlsx_extractor import extract_xlsx_to_json
                    data = extract_xlsx_to_json(tmp_file_path)
                    
                    # JSONファイルとして出力（出力先は Tmp フォルダ）
                    from infrastructure.json_writer import write_json_output
                    json_filepath = write_json_output(data, out_filename)
                    json_file_paths.append(f"{file} => {json_filepath}")
            
            if json_file_paths:
                msg = "以下の XLSX ファイルから JSON 出力が作成されました:\n" + "\n".join(json_file_paths)
            else:
                msg = "選択されたファイルの中に XLSX ファイルはありませんでした。"
            messagebox.showinfo("出力完了", msg)
            self.status_label.config(text="次の作業: 合算処理を行うか、再度ファイルを選択するか、終了してください")
        except Exception as e:
            logger.error("XLSX抽出処理中にエラー: %s", e)
            messagebox.showerror("エラー", f"XLSX抽出処理中にエラーが発生しました:\n{e}")
    
    def merge_json_files(self):
        """
        Tmpフォルダ内の JSON ファイルを、keywords に基づく単位ごとに合算し、
        各合算結果を OUT フォルダに output_{unit}.json として出力します。
        合算処理は、各 JSON ファイル内の全シート・全グループの各行について、
        「グループ」「指図書No」「補足」を主キーとし、「時間」を合計します。
        """
        try:
            from infrastructure.json_merger import merge_json_files_by_unit
            output_paths = merge_json_files_by_unit(self.keywords)
            if output_paths:
                msg_lines = [f"{unit}: {path}" for unit, path in output_paths.items()]
                msg = "合算結果:\n" + "\n".join(msg_lines)
            else:
                msg = "合算対象となる JSON ファイルが見つかりませんでした。"
            messagebox.showinfo("合算完了", msg)
            self.status_label.config(text="次の作業: 合算処理完了。再度ファイルを選択するか、終了してください")
        except Exception as e:
            logger.error("合算処理中にエラー: %s", e)
            messagebox.showerror("エラー", f"合算処理中にエラーが発生しました:\n{e}")
