# Walkthrough - SQL Execution Script, Tray Icon, Character Encoding & NL Keyword Parsing Resolution

This document summarizes the changes made to resolve the tray icon visibility, SQL execution script display, database metadata encoding, terminal character set, and natural language query keyword parsing issues in OHSUNG ERP Bot.

---

## 1. System Tray Icon and Close-to-Tray Bug Fix (Tray Minimization)
* **Problem**: Clicking the top-right `[V]` button hid the GUI window, but the program appeared to terminate because no tray icon was visible in the Windows taskbar.
* **Cause**: In `client/main.py`, the tray icon paths were configured to look directly inside the project root directory, whereas the logo files (e.g., `ohsung_mark_256.png`, `mark_512.png`) were stored inside the `image/` subdirectory. Consequently, the tray icon failed to load, leading to a blank/invisible icon registration on Windows.
* **Resolution**: Updated `icon_names` in `client/main.py` to search the `image/` folder first:
  ```python
  icon_names = [
      "image/ohsung_mark_256.png",
      "image/mark_512.png",
      "ohsung_mark.png",
      "ohsung_mark_256.png",
      "mark.png",
      "mark.bmp"
  ]
  ```
  Now, the red-themed Ohsung logo correctly renders in the Windows system tray. Double-clicking the tray icon or selecting the context menu toggle restores the window, preventing accidental app termination.

---

## 2. SQL Column Alias Encoding Correction (Database Metadata)
* **Problem**: In the SQL query result table headers and query script details, Korean characters were corrupted (e.g., `'특성명'` was rendered as `'Ư'`).
* **Cause**: In `server/services/db_service.py`, although basic char/wchar decoding was configured for pyodbc, wide-character metadata (`SQL_WMETADATA`) was not explicitly decoded. Windows environments under different locales interpreted SQL Server's returned metadata using default system encoding (CP949) rather than UTF-16, mangling the string values.
* **Resolution**: Added the `SQL_WMETADATA` decoder to `db_service.py`:
  ```python
  if hasattr(pyodbc, 'SQL_WMETADATA'):
      conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='utf-16')
  ```
  This immediately fixed the character encoding of SQL column aliases, ensuring database keys such as `'특성명'` and `'특성코드'` are decoded correctly into Python unicode strings.

---

## 3. Terminal output & Process UTF-8 Mode Enforcement
* **Problem**: Running Python test scripts in VS Code PowerShell or running uvicorn in the background resulted in broken Korean log output in the terminal due to character page mismatches (CP949 vs. UTF-8).
* **Resolution**:
  * Added session encoding commands at the beginning of `run.ps1` to force UTF-8 console output:
    ```powershell
    [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    ```
  * Injected environment variables in `run.ps1` and `실행.bat` to run Python in UTF-8 mode:
    ```powershell
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    ```
    This ensures that Python always uses UTF-8 encoding for standard streams and log files regardless of the active Windows system code page.

---

## 4. Port Conflict Resolution & Verification
* **Resolution**:
  * Unified the server and client connection endpoints on port **`8002`** (via `.env` configs) to avoid conflicts with port `8001` (often locked by background processes).
  * Ran direct API testing (`test_final.py`) which verified:
    * `Health: {'status': 'ok'}`
    * `intent: part_tcod_search`
    * `count: 5`
    * Correctly formatted SQL scripts returned and rendered without parameter variables.

---

## 5. Natural Language Query Keyword Expansion (부품특성 C parsing)
* **Problem**: In natural language search mode, queries like `"부품특성 C"` or `"[ 부품특성 C ]"` matched the intent `part_tcod_search` using the general keyword `"특성"`. However, the prefix `"부품"` was left behind, resulting in the search variable `@as_find` being parsed as `"부품 C"` instead of `"C"`.
* **Resolution**: Added `"부품특성코드"` and `"부품특성"` to the category keyword list for `"part_tcod_search"` in `server/services/intent_matcher.py` before `"특성"`. This ensures `"부품특성"` is fully matched and stripped from the input message, leaving only `"C"` (and stripping outer brackets) as the search value.
* **Verification**: Verified using API endpoint queries that:
  * `"부품특성 C"` maps to `fact: 'Y6'`, `as_find: 'C'`, returning 19 results from the database.
  * `"[ 부품특성 C ]"` also correctly maps to `fact: 'Y6'`, `as_find: 'C'`.
