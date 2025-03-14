import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os
import shutil
from use_cases.file_search_usecase import get_matched_files
from config import TMP_FOLDER, KEYWORDS, OUT_FOLDER
from infrastructure.file_copier import copy_xlsx_file
from infrastructure.json_writer import write_json_output
from infrastructure.xlsx_extractor import extract_xlsx_to_json
from infrastructure.json_merger import merge_json_files_by_unit
from infrastructure.clear_folder import clear_folder_contents
from infrastructure.json_to_csv import convert_json_file_to_csv  # 追加

logger = logging.getLogger(__name__)

class ResultMergeUI(tk.Frame):
    def __init__(self, root, keywords):
        super().__init__(root, width=600, height=400, borderwidth=1, relief='groove')
        self.root = root
        self.keywords = keywords  # 例: ["金子", "本間"]
        self.base_folder = None   # ユーザーが選択した INフォルダのパス
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
        self.csv_button = tk.Button(button_frame, text="CSV変換", command=self.convert_json_to_csv)
        self.csv_button.pack(side=tk.RIGHT, padx=5)  # 新規ボタン「CSV変換」
        
        
        # --- 中央：ステータスバー ---
        self.status_label = tk.Label(self, text="次の作業: フォルダを選択してください", anchor='w', relief=tk.SUNKEN)
        self.status_label.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        # --- 下部：ファイル一覧 (スクロールバー付き) ---
        list_frame = tk.Frame(self)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(list_frame, text="ファイル一覧").pack(anchor='w')
        listbox_frame = tk.Frame(list_frame, height=300)
        listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
    
    def select_folder(self):
        # TMP_FOLDER の中身のみ削除
        if os.path.exists(TMP_FOLDER):
            try:
                clear_folder_contents(TMP_FOLDER)
                logger.info("TMP フォルダ内の内容を削除しました: %s", TMP_FOLDER)
            except Exception as e:
                logger.error("TMP フォルダ内内容削除に失敗: %s", e)
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.base_folder = folder_path
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
            logger.error("ファイルリスト取得中にエラー: %s", e)
    
    def show_selected_info(self):
        try:
            # Outフォルダの内容を削除（Outフォルダ自体は残す）
            clear_folder_contents(OUT_FOLDER)
            
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
                    tmp_file_path = copy_xlsx_file(in_file_path, self.base_folder)
                    base_name, _ = os.path.splitext(os.path.basename(tmp_file_path))
                    out_filename = f"{base_name}.json"
                    data = extract_xlsx_to_json(tmp_file_path)
                    json_filepath = write_json_output(data, out_filename)
                    json_file_paths.append(f"{file} => {json_filepath}")
            if json_file_paths:
                msg = "以下の XLSX ファイルから JSON 出力が作成されました:\n" + "\n".join(json_file_paths)
            else:
                msg = "選択されたファイルの中に XLSX ファイルはありませんでした。"
            messagebox.showinfo("出力完了", msg)
            # 自動的に合算処理も実行
            self.merge_json_files()
            self.status_label.config(text="次の作業: 合算処理完了。再度ファイルを選択するか、終了してください")
        except Exception as e:
            logger.error("XLSX抽出処理中にエラー: %s", e)
            messagebox.showerror("エラー", f"XLSX抽出処理中にエラーが発生しました:\n{e}")
    
    def merge_json_files(self):
        try:
            # Outフォルダの内容を削除（Outフォルダ自体は残す）
            clear_folder_contents(OUT_FOLDER)
            
            output_path = merge_json_files_by_unit(self.keywords)
            if output_path:
                msg = f"合算結果の JSON が作成されました:\n{output_path}"
            else:
                msg = "合算対象となる JSON ファイルが見つかりませんでした。"
            messagebox.showinfo("合算完了", msg)
            self.status_label.config(text="次の作業: 合算処理完了。再度ファイルを選択するか、終了してください")
        except Exception as e:
            logger.error("合算処理中にエラー: %s", e)
            messagebox.showerror("エラー", f"合算処理中にエラーが発生しました:\n{e}")
    
    def convert_json_to_csv(self):
        """
        OUT_FOLDER 内の各 JSON ファイルを CSV に変換します。
        変換後の CSV ファイルは、JSON ファイル名と同一のベース名に拡張子 .csv を付与し、OUT_FOLDER に保存します。
        """
        from infrastructure.json_to_csv import convert_json_file_to_csv
        csv_file_paths = []
        for filename in os.listdir(OUT_FOLDER):
            if filename.lower().endswith(".json"):
                json_filepath = os.path.join(OUT_FOLDER, filename)
                base_name, _ = os.path.splitext(filename)
                csv_filename = f"{base_name}.csv"
                csv_filepath = os.path.join(OUT_FOLDER, csv_filename)
                success = convert_json_file_to_csv(json_filepath, csv_filepath)
                if success:
                    csv_file_paths.append(f"{filename} => {csv_filename}")
        if csv_file_paths:
            msg = "以下の JSON ファイルから CSV 変換が行われました:\n" + "\n".join(csv_file_paths)
        else:
            msg = "変換対象となる JSON ファイルが見つかりませんでした。"
        messagebox.showinfo("CSV変換完了", msg)
        self.status_label.config(text="次の作業: CSV変換完了。再度ファイルを選択するか、終了してください")
