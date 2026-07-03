# Design Document: Table Column Sizing and Horizontal Scrollbar Implementation

- **Date**: 2026-07-01
- **Topic**: Fit-to-contents table columns with horizontal scrollbar in PySide6 ERP chatbot.
- **Approved Approach**: Approach A (ResizeToContents for data columns, fixed 40px for NO. column, minimum column size, and scrollbar as needed).

## 1. Requirements & Intent
- **Header Visibility**: Ensure header text is fully readable and not truncated.
- **Data-dependent Width**: Size columns dynamically based on the length of the longest text in both the headers and the cells.
- **Horizontal Scrolling**: If the total width of all columns exceeds the width of the bottom result panel, show a horizontal scrollbar.
- **Fixed Index Column**: Keep the 'NO.' column at a fixed width of `40px`.

## 2. Technical Details & Configuration
In `client/ui/main_window.py`:

### Table Initialization (`init_ui`)
- Change the horizontal header's resize mode. Instead of:
  ```python
  self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  ```
  We will set:
  ```python
  self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
  ```
- Explicitly set the horizontal scrollbar policy to `Qt.ScrollBarAsNeeded`:
  ```python
  self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
  ```
- Set a minimum section size for headers (e.g. `60px` or `70px`) to prevent columns with tiny content from becoming too narrow and cutting off header words:
  ```python
  self.table_widget.horizontalHeader().setMinimumSectionSize(60)
  ```

### Data Loading (`update_table_view`)
- During the first page load (`new_results_offset == 0`):
  - Set the first column (`NO.`) to fixed resize mode and width `40px`:
    ```python
    self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
    self.table_widget.setColumnWidth(0, 40)
    ```
  - Set all subsequent data columns to `QHeaderView.ResizeToContents`:
    ```python
    for c in range(1, len(columns) + 1):
        self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
    ```

## 3. Verification Plan
- **Mock Data Test**: Query different intents (Vendor, Model, Product Code, Part Detail, Part Characteristic) to populate columns of varying lengths.
- **UI Visual Check**: Run the client application, query data, and verify:
  1. The "NO." column width remains exactly 40px.
  2. All other columns are adjusted to match the longest item (header or data).
  3. A horizontal scrollbar appears when the table width is smaller than the columns' total width.
  4. Column headers are fully readable.
