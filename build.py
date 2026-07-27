import PyInstaller.__main__
import os
import shutil

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

tools_dir = os.path.join(current_dir, "tools")
add_data_list = [f'--add-data={os.path.join(current_dir, "assets")};assets']
if os.path.exists(tools_dir):
    add_data_list.append(f'--add-data={tools_dir};tools')

temp_dist_dir = os.path.join(current_dir, "build", "dist_temp")
final_dist_dir = os.path.join(current_dir, "dist", "Studio0808_Downloader_V20260727")

cmd_args = [
    'Studio0808_Downloader_V20260727.py',
    '--name=Studio0808_Downloader_V20260727',
    '--windowed',
    '--noconfirm',
    '--clean',
    f'--distpath={temp_dist_dir}',
    
    # Exclude heavy/unnecessary packages explicitly to ensure minimum size
    '--exclude-module=torch',
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=scipy',
    '--exclude-module=pandas',
    '--exclude-module=PySide6',
    '--exclude-module=PyQt5',
    '--exclude-module=PyQt6',
] + add_data_list + [
    # CustomTkinter files
    '--collect-all=customtkinter',
    '--collect-all=darkdetect',
    
    # Icon
    f'--icon={os.path.join(current_dir, "assets", "app.ico")}'
]

print("[Build] 正在啟動安全打包程序 (獨立暫存區打包，不影響現有 dist 資料)...")
PyInstaller.__main__.run(cmd_args)

# Non-destructive copy/sync to dist/Studio0808_Downloader_V20260727
src_build_output = os.path.join(temp_dist_dir, "Studio0808_Downloader_V20260727")
if os.path.exists(src_build_output):
    os.makedirs(final_dist_dir, exist_ok=True)
    print(f"\n[Sync] 正在將新版打包產物安全同步至目標目錄:\n   {final_dist_dir}\n   (現有的 .zip 檔、Outputs 資料夾及其他檔案均全數完整保留)")
    
    try:
        for item in os.listdir(src_build_output):
            s_path = os.path.join(src_build_output, item)
            d_path = os.path.join(final_dist_dir, item)
            if os.path.isdir(s_path):
                shutil.copytree(s_path, d_path, dirs_exist_ok=True)
            else:
                shutil.copy2(s_path, d_path)
                
        print("[Sync] 打包與非破壞性同步成功！現有 dist 資料夾內的所有歷史打包檔案已完整保留。")
    except Exception as e:
        print(f"[Sync Warning] 同步過程出現提示: {e}")

