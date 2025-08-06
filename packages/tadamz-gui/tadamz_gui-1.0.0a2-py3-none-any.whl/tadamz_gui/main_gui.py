import sys
from os import path

import emzed
import emzed.gui
import tadamz
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import tadamz_gui
from tadamz_gui.select_wf_type import WFTypeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("tadaMZ GUI")
        self.setFixedSize(250, 200)

        # Show logo
        assets_dir = path.join(path.dirname(__file__), "assets")
        logo_svg_widget = QSvgWidget(f"{assets_dir}/Logo.svg")
        logo_svg_widget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        # logo_svg_widget.setFixedHeight(80)

        button_setup = QPushButton("Setup workflow")
        button_setup.clicked.connect(self.show_setup_window)

        button_inspect = QPushButton("Inspect results")
        button_inspect.clicked.connect(self.inspect_results)

        versions = {
            "tadamz_gui": tadamz_gui.__version__,
            "tadamz": tadamz.__version__,
            "emzed": emzed.__version__,
            "emzed.gui": emzed.gui.__version__,
        }
        versions_text = "\n".join(f"{key}={value}" for key, value in versions.items())
        label_versions = QLabel(f"Versions:\n{versions_text}")
        label_versions_font = QFont()
        label_versions_font.setPointSize(10)
        label_versions.setFont(label_versions_font)

        layout_buttons = QVBoxLayout()
        layout_buttons.addWidget(button_setup)
        layout_buttons.addWidget(button_inspect)

        layout_logo_versions = QHBoxLayout()
        layout_logo_versions.addWidget(logo_svg_widget)
        layout_logo_versions.addWidget(label_versions)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_buttons)
        main_layout.addLayout(layout_logo_versions)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def show_setup_window(self):
        self.window_setup = WFTypeWindow()
        self.window_setup.show()

    def inspect_results(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Open existing result table",
            filter="Table (*.table)",
            options=options,
        )

        if file:
            try:
                t = emzed.io.load_table(file)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error loading table", f"The table could not be opened: {e}"
                )
            else:
                emzed.gui.inspect(t)

    def closeEvent(self, event):
        # Required to close the app properly, otherwise a process from emzed.gui remains running
        from emzed_gui import qapplication

        qapplication().quit()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
