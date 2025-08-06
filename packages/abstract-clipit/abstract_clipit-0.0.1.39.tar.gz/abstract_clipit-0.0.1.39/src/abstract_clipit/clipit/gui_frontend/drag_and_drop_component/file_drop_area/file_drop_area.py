from .get_file_drop import *
from ..imports import *
from abstract_utilities import get_media_exts, eatOuter
import os
import traceback
from PyQt5 import QtCore, QtGui, QtWidgets
from typing import List, Set, Optional
import ast

logger = get_logFile('clipit_logs')

def unlist(obj):
    if obj and isinstance(obj, list):
        obj = obj[0]
    return obj
def get_all_dir_pieces(file_paths: List[str]) -> List[str]:
    """Extract unique directory components, excluding root-like components."""
    all_pieces = set()
    for file_path in file_paths:
        path = Path(file_path)
        for parent in path.parents:
            name = parent.name
            if name:
                all_pieces.add(name)
    return sorted(list(all_pieces))
def is_string_in_dir(path,strings):
    dirname =  path
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
    pieces = [pa for pa in dirname.split('/') if pa and pa in strings]
    logger.info(f"pieces = {pieces}\nstrings == {strings}")
    if pieces:
        return True
    return False
def is_in_exts(path,exts,visible_dirs):
    logger.info(f"path = {path}\nexts == {exts}")
    if is_string_in_dir(path,visible_dirs):
        return True
    if os.path.isdir(path):
        return True
    ext = os.path.splitext(path)[1].lower()
    if ext in exts:
        return True
    return 
class FileDropArea(QtWidgets.QWidget):
    function_selected = QtCore.pyqtSignal(dict)
    file_selected = QtCore.pyqtSignal(dict)

    def __init__(self, log_widget: QtWidgets.QTextEdit, view_widget=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.log_widget = log_widget
        self.view_widget = view_widget
        self.dir_pieces = []
        self.ext_checks: dict[str, QtWidgets.QCheckBox] = {}
        self.dir_checks: dict[str, QtWidgets.QCheckBox] = {}
        self._last_raw_paths: list[str] = []
        self.functions: list[dict] = []
        self.python_files: list[dict] = []
        self.combined_text_lines: dict[str, dict] = {}
        self.allowed_extensions = DEFAULT_ALLOWED_EXTS
        self.unallowed_extensions = DEFAULT_UNALLOWED_EXTS
        self.exclude_types = DEFAULT_EXCLUDE_TYPES
        self.exclude_dirs = DEFAULT_EXCLUDE_DIRS | {"backup", "backups"}
        self.exclude_file_patterns = DEFAULT_EXCLUDE_PATTERNS
        self.exclude_dir_patterns = set()  # New: store user-specified dir patterns

        # Main vertical layout
        lay = QtWidgets.QVBoxLayout(self)

        # 1) “Browse Files…” button
        browse_btn = get_push_button(text="Browse Files…", action=self.browse_files)
        self.view_toggle = 'array'

        # 2) Extension-filter row
        self.ext_row = QtWidgets.QScrollArea(widgetResizable=True)
        self.ext_row.setFixedHeight(45)
        self.ext_row.setVisible(False)
        self.ext_row_w = QtWidgets.QWidget()
        self.ext_row.setWidget(self.ext_row_w)
        self.ext_row_lay = QtWidgets.QHBoxLayout(self.ext_row_w)
        self.ext_row_lay.setContentsMargins(4, 4, 4, 4)
        self.ext_row_lay.setSpacing(10)
        self._selected_text: dict[str, str] = {}

        # 3) Directory-filter row (new)
        # 3) Directory-filter row (checkboxes)
        self.dir_row = QtWidgets.QScrollArea(widgetResizable=True)
        self.dir_row.setFixedHeight(45)
        self.dir_row.setVisible(False)
        self.dir_row_w = QtWidgets.QWidget()
        self.dir_row.setWidget(self.dir_row_w)
        self.dir_row_lay = QtWidgets.QHBoxLayout(self.dir_row_w)
        self.dir_row_lay.setContentsMargins(4, 4, 4, 4)
        self.dir_row_lay.setSpacing(10)



        # 4) Tab widget to switch between “List View” and “Text View”
        self.view_tabs = QtWidgets.QTabWidget()

        # List View Tab
        list_tab = QtWidgets.QWidget()
        list_layout = get_layout(parent=list_tab)
        self.function_list = QtWidgets.QListWidget()
        self.function_list.setVisible(False)
        self.function_list.setAcceptDrops(False)
        self.function_list.itemClicked.connect(self.on_function_clicked)
        self.python_file_list = QtWidgets.QListWidget()
        self.python_file_list.setVisible(False)
        self.python_file_list.setAcceptDrops(False)
        self.python_file_list.itemClicked.connect(self.on_python_file_clicked)
        add_widgets(list_layout, {"widget": self.python_file_list}, {"widget": self.function_list})
        self.view_tabs.addTab(list_tab, "List View")

        # Text View Tab
        text_tab = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_tab)
        self.text_view = QtWidgets.QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setVisible(False)
        self.text_view.setAcceptDrops(False)
        add_widgets(text_layout, {"widget": self.text_view})
        self.view_tabs.addTab(text_tab, "Text View")

        # 5) Status label
        self.status = QtWidgets.QLabel("No files selected.", alignment=QtCore.Qt.AlignCenter)
        self.status.setStyleSheet("color: #333; font-size: 12px;")

        add_widgets(
            lay,
            {"widget": browse_btn, "kargs": {"alignment": QtCore.Qt.AlignHCenter}},
            {"widget": self.dir_row},  # Add directory filter row
            {"widget": self.ext_row},
            {"widget": self.view_tabs},
            {"widget": self.status}
        )

        # Initialize dir patterns from input
        self._update_dir_patterns()

    def _update_dir_patterns(self):
        """Update self.exclude_dir_patterns from dir_input text."""
        text = self.dir_checks
        if text:
            self.exclude_dir_patterns = self.dir_checks
        else:
            self.exclude_dir_patterns = set()
        self.exclude_dir_patterns.update(self.exclude_dirs)  # Include defaults
    def _rebuild_ext_row(self, paths: list[str]) -> None:
        exts = {os.path.splitext(p)[1].lower() for p in paths if os.path.isfile(p)}
        exts.discard("")
        self._log(f"Found extensions: {exts}")
        if not exts:
            self.ext_row.setVisible(False)
            self.ext_checks.clear()
            return
        self._clear_layout(self.ext_row_lay)
        new_checks: dict[str, QtWidgets.QCheckBox] = {}
        for ext in sorted(exts):
            cb = QtWidgets.QCheckBox(ext)
            prev_cb = self.ext_checks.get(ext)
            cb.setChecked(prev_cb.isChecked() if prev_cb else True)
            cb.stateChanged.connect(self._apply_ext_filter)
            self.ext_row_lay.addWidget(cb)
            new_checks[ext] = cb
        self.ext_row_lay.addStretch()
        self.ext_checks = new_checks
        self.ext_row.setVisible(True)
    def _rebuild_dir_row(self, paths: list[str]) -> None:
        """Rebuild directory filter row with checkboxes for directory pieces."""
        self.dir_pieces = get_all_dir_pieces(paths)
        self.dir_pieces = set(list(self.dir_pieces))
        dir_pieces = self.dir_pieces
        self._log(f"Directory pieces: {dir_pieces}")
        if not dir_pieces:
            self.dir_row.setVisible(False)
            self.dir_checks.clear()
            self._log("No directory pieces found; hiding dir_row.")
            return
        self._clear_layout(self.dir_row_lay)
        new_checks: dict[str, QtWidgets.QCheckBox] = {}
        for dir_name in dir_pieces:
            cb = QtWidgets.QCheckBox(dir_name)
            prev_cb = self.dir_checks.get(dir_name)
            cb.setChecked(prev_cb.isChecked() if prev_cb else False)
            cb.stateChanged.connect(self._apply_ext_filter)
            self.dir_row_lay.addWidget(cb)
            new_checks[dir_name] = cb
        self.dir_row_lay.addStretch()
        self.dir_checks = new_checks
        self.dir_row.setVisible(True)
        
        #self._log(f"Directory row visible: True, checkboxes: {list(new_checks.keys())}")
    




    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        try:
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in make_list(urls)]
            if not paths:
                raise ValueError("No local files detected on drop.")
            self.process_files(paths)
        except Exception as e:
            tb = traceback.format_exc()
            self.status.setText(f"⚠️ Error during drop: {e}")
            self._log(f"dropEvent ERROR:\n{tb}")

    def filter_paths(self, paths: list[str]) -> list[str]:
        filtered = collect_filepaths(
            paths,
            allowed_exts=self.allowed_extensions,
            unallowed_exts=self.unallowed_extensions,
            exclude_types=self.exclude_types,
            exclude_dirs=self.exclude_dir_patterns,  # Use dynamic dir patterns
            exclude_file_patterns=self.exclude_file_patterns
        )
        self._log(f"_filtered_file_list returned {len(filtered)} path(s)")
        if not filtered:
            self.status.setText("⚠️ No valid files detected in drop.")
            self._log("No valid paths after filtering.")
            return []
        self._log(f"Proceeding to process {len(filtered)} file(s).")
        return filtered

    def get_contents_text(self, file_path: str, idx: int = 0, filtered_paths: list[str] = []):
        basename = os.path.basename(file_path)
        filename, ext = os.path.splitext(basename)
        if ext not in self.unallowed_extensions:
            header = f"=== {file_path} ===\n"
            footer = "\n\n――――――――――――――――――\n\n"
            info = {
                'path': file_path,
                'basename': basename,
                'filename': filename,
                'ext': ext,
                'text': "",
                'error': False,
                'visible': True
            }
            try:
                body = read_file_as_text(file_path) or ""
                if isinstance(body, list):
                    body = "\n".join(body)
                info["text"] = [header, body, footer]
                if ext == '.py':
                    self._parse_functions(file_path, str(body))
            except Exception as exc:
                info["error"] = True
                info["text"] = f"[Error reading {basename}: {exc}]\n"
                self._log(f"Error reading {file_path} → {exc}")
            return info

    def process_files(self, paths: list[str] = None) -> None:
        paths = paths or []
        self._last_raw_paths = paths
        filtered = self.filter_paths(paths)
        if not filtered:
            return
        self._rebuild_ext_row(filtered)
        self._rebuild_dir_row(filtered)
        filtered_paths=[]
        if self.ext_checks or self.dir_checks:
            visible_exts = {ext for ext, cb in self.ext_checks.items() if cb.isChecked()}
            visible_dirs = {di for di, cb in self.dir_checks.items() if cb.isChecked()}
            self._log(f"Visible extensions: {visible_exts}")
            filtered_paths = [
                p for p in filtered
                if (os.path.isdir(p) or os.path.splitext(p)[1].lower() in visible_exts) and not is_string_in_dir(p,list(visible_dirs))
            ]
        else:
            filtered_paths  = filtered
        if not filtered_paths:
            self.text_view.clear()
            self.status.setText("⚠️ No files match current extension filter.")
            return
        self.status.setText(f"Reading {len(filtered_paths)} file(s)…")
        QtWidgets.QApplication.processEvents()
        self.combined_text_lines = {}
        self.functions = []
        self.python_files = []
        for idx, p in enumerate(filtered_paths, 1):
            info = self.get_contents_text(p, idx, filtered_paths)
            if info:
                self.combined_text_lines[p] = info
                if info['ext'] == '.py':
                    self.python_files.append(info)
        self._populate_list_view()
        self._populate_text_view()
        self.status.setText("Files processed. Switch tabs to view.")


    def _apply_ext_filter(self) -> None:
        if self._last_raw_paths:
            self.process_files(self._last_raw_paths)

    def populate_python_view(self) -> None:
        self.python_file_list.clear()
        all_paths = [info['path'] for info in self.python_files]
        filtered_set = set(self.filter_paths(self._last_raw_paths))
        for p in all_paths:
            item = QtWidgets.QListWidgetItem(os.path.basename(p))
            item.setData(QtCore.Qt.UserRole, p)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked if p in filtered_set else QtCore.Qt.Unchecked)
            self.python_file_list.addItem(item)
        self.python_file_list.setVisible(bool(all_paths))

    def _populate_list_view(self) -> None:
        self.function_list.clear()
        if self.functions:
            for func in self.functions:
                itm = QtWidgets.QListWidgetItem(f"{func['name']} ({func['file']})")
                itm.setFlags(itm.flags() | QtCore.Qt.ItemIsUserCheckable)
                itm.setCheckState(QtCore.Qt.Unchecked)
                self.function_list.addItem(itm)
            self.function_list.setVisible(True)
        else:
            self.function_list.setVisible(False)
        self.populate_python_view()

    def _populate_text_view(self) -> None:
        if not self.combined_text_lines:
            self.text_view.clear()
            self.text_view.setVisible(False)
            return
        parts = []
        for path, info in self.combined_text_lines.items():
            if not info.get('visible', True):
                continue
            lines = info['text']
            if self.view_toggle != 'print':
                lines = [lines[0], repr(lines[1]), lines[-1]]
            seg = "\n".join(lines)
            parts.append(seg)
        final = "\n\n".join(parts)
        self.text_view.setPlainText(final)
        self.text_view.setVisible(bool(final))
        copy_to_clipboard(final)

    def _toggle_populate_text_view(self, view_toggle=None) -> None:
        if view_toggle:
            self.view_toggle = view_toggle
        self._populate_text_view()

    def _parse_functions(self, file_path: str, text: str) -> None:
        try:
            tree = ast.parse(text, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_code = "\n".join(text.splitlines()[node.lineno-1:node.end_lineno])
                    imports = self._extract_imports(tree)
                    self.functions.append({
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno,
                        'code': func_code,
                        'imports': imports
                    })
        except SyntaxError as e:
            self._log(f"Syntax error in {file_path}: {e}")

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        return imports

    def on_function_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        index = self.function_list.row(item)
        function_info = self.functions[index]
        self.function_selected.emit(function_info)

    def on_python_file_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        index = self.python_file_list.row(item)
        file_info = self.python_files[index]
        self.file_selected.emit(file_info)

    def map_function_dependencies(self, function_info: dict) -> None:
        combined_lines = []
        combined_lines.append(f"=== Function: {function_info['name']} ===\n")
        combined_lines.append(function_info['code'])
        combined_lines.append("\n\n=== Imports ===\n")
        combined_lines.extend(function_info['imports'])
        project_files = collect_filepaths(
            [os.path.dirname(function_info['file'])],
            exclude_dirs=self.exclude_dir_patterns,
            exclude_file_patterns=self.exclude_file_patterns
        )
        combined_lines.append("\n\n=== Project Reach ===\n")
        for file_path in project_files:
            if file_path != function_info['file'] and file_path.endswith('.py'):
                combined_lines.append(f"--- {file_path} ---\n")
                try:
                    text = read_file_as_text(file_path)
                    combined_lines.append(text)
                except Exception as exc:
                    combined_lines.append(f"[Error reading {os.path.basename(file_path)}: {exc}]\n")
                combined_lines.append("\n")
        QtWidgets.QApplication.clipboard().setText("\n".join(combined_lines))
        self.status.setText(f"✅ Copied function {function_info['name']} and dependencies to clipboard!")
        self._log(f"Copied function {function_info['name']} with dependencies")

    def map_import_chain(self, file_info: dict) -> None:
        try:
            module_paths, imports = get_py_script_paths([file_info['path']])
            combined_lines = []
            combined_lines.append(f"=== Import Chain for {file_info['path']} ===\n")
            combined_lines.append("Modules:\n")
            if module_paths:
                combined_lines.extend(f"- {p}" for p in module_paths)
            else:
                combined_lines.append("- None\n")
            combined_lines.append("\nImports:\n")
            if imports:
                combined_lines.extend(f"- {imp}" for imp in imports)
            else:
                combined_lines.append("- None\n")
            QtWidgets.QApplication.clipboard().setText("\n".join(combined_lines))
            self.status.setText(f"✅ Copied import chain for {os.path.basename(file_info['path'])} to clipboard!")
            self._log(f"Copied import chain for {file_info['path']}")
        except Exception as e:
            tb = traceback.format_exc()
            self.status.setText(f"⚠️ Error mapping import chain: {e}")
            self._log(f"map_import_chain ERROR:\n{tb}")

    def browse_files(self) -> None:
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Files to Copy",
            "",
            "All Supported Files (" + " ".join(f"*{ext}" for ext in self.allowed_extensions) + ");;All Files (*)"
        )
        if files:
            filtered = self.filter_paths(files)
            if filtered:
                self.process_files(filtered)

    def _log(self, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        logger.info(f"[{timestamp}] {message}")
        self.log_widget.append(f"[{timestamp}] {message}")

    def _clear_layout(self, layout: QtWidgets.QLayout) -> None:
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
