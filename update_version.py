import os
import datetime

def increment_version():
    today_str = datetime.date.today().strftime("%Y%m%d")
    
    # 이 스크립트 파일이 위치한 프로젝트 루트 경로에서 version.txt 파일을 관리합니다.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(base_dir, "version.txt")
    
    current_version = "ver.20260706.001"  # 기본 초깃값
    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("ver."):
                    current_version = content
        except Exception:
            pass
            
    # 버전을 파싱합니다 (형식: ver.YYYYMMDD.XXX)
    parts = current_version.split(".")
    if len(parts) == 3 and parts[0] == "ver":
        file_date = parts[1]
        try:
            counter = int(parts[2])
        except ValueError:
            counter = 0
            
        if file_date == today_str:
            new_counter = counter + 1
        else:
            new_counter = 1
    else:
        new_counter = 1
        
    new_version = f"ver.{today_str}.{new_counter:03d}"
    
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(new_version)
        
    print(f"Version updated to: {new_version}")
    return new_version

if __name__ == "__main__":
    increment_version()
