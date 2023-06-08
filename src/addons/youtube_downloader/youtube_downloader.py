# Widget and functions for downloading youtube videos
# the widget is triggered with key shortcut: Ctrl+Shift+Y
import os
import sys

import json
from pynput import keyboard

from traceback import format_exc

from typing import Optional

import ssl

from pytube import YouTube

from PyQt5.QtWidgets import (
    QProgressBar,
    QApplication,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QComboBox,
    QWidget,
    QLabel,
)

from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QLinearGradient, QKeySequence

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.utils import get_font  # pylint: disable=import-error
from ui.entry_box import Entry  # pylint: disable=import-error
from ui.settings import UI_SCALE  # pylint: disable=import-error
from ui.base_window import BaseWindow  # pylint: disable=import-error
from ui.dialog import ConfirmationDialog, BaseDialog  # pylint: disable=import-error
from ui.custom_button import RedButton, GrnButton, YelButton, TextButton  # pylint: disable=import-error

from addon import AddOnBase

class RoundedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QProgressBar {
                border-radius: 10px;
                border: 0px solid grey;
            }

            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 red, stop: 0.5 orange,
                                                  stop:1 green);
                border-radius: 10px;
                border: 0px solid black;
            }

        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background
        bg_rect = self.rect().adjusted(1, 1, -1, -1)

        # remove border
        painter.setPen(Qt.NoPen)

        # Draw the progress bar
        progress_rect = bg_rect.adjusted(0, 0, -int(bg_rect.width() * (1 - self.value() / self.maximum())), 0)

        # Create the gradient
        gradient = QLinearGradient(QPointF(progress_rect.left(), progress_rect.top()), QPointF(progress_rect.right(), progress_rect.top()))
        gradient.setColorAt(0, Qt.red)
        gradient.setColorAt(0.5, Qt.yellow)
        gradient.setColorAt(1, Qt.green)

        painter.setBrush(gradient)
        painter.drawRoundedRect(progress_rect, 10, 10)

    def minimumSizeHint(self):
        return self.sizeHint()

def get_available_videos(url: str, progress: pyqtSignal = None) -> dict:
    """Get a list of available videos with coresponding resolutions for a YouTube URL.

    Args:
        url (str): URL of the video

    Returns:
        dict: Dictionary with key as video type and value as list of resolutions
        Ex: {
            '3gpp': ['144p'],
            'mp4': [None, '144p', '240p', '360p', '480p', '720p', '1080p'],
            'webm': [None, '144p', '240p', '360p', '480p', '720p', '1080p']
        }
    """

    try:
        ssl._create_default_https_context = ssl._create_stdlib_context  # pylint: disable=protected-access
        yt_downloader = YouTube(url)

        available_videos = {}
        for stream in yt_downloader.streams:
            video_type = stream.mime_type.split('/')[1]
            if video_type not in available_videos:
                available_videos[video_type] = []
            available_videos[video_type].append(stream.resolution)

        # remove duplicatesfrom the list of resolutions
        for video_type in available_videos:
            available_videos[video_type] = list(set(available_videos[video_type]))
            available_videos[video_type].sort(key=lambda x: int(x[:-1]) if x else 0)
        return available_videos
    except Exception as err:
        print(f"Error getting available videos: {err}\n{format_exc()}")
        return {}

def download_youtube_video(
        url: str,
        download_path: str = os.path.join(os.path.expanduser("~"), "Downloads"),
        video_type: str = "mp4",
        resolution: str = "720p",
        progress: pyqtSignal = None,
        filesize: pyqtSignal = None) -> int:
    """Download a youtube video given its url, download_path, video_type and resolution.

    Args:
        url (str): URL of the video
        download_path (str): Path to save the video
        video_type (str): Video type (mp4, webm, ...)
        resolution (str): Video resolution (720p, 480p, ...)
        progress (pyqtSignal): Signal to emit progress

    Returns:
        int: 0 if the video is downloaded successfully, 1 otherwise.
    """

    try:
        progress.emit(1, 1, 1)
        ssl._create_default_https_context = ssl._create_stdlib_context  # pylint: disable=protected-access
        yt_downloader1 = YouTube(url)

        # check if the video is available in the specified resolution
        if not yt_downloader1.streams.filter(file_extension=video_type, resolution=resolution):
            print(f"Video not available in {resolution} resolution")
            return 1
        progress.emit(2, 2, 2)
        # add _resolution to the filename
        video_name = yt_downloader1.streams.filter(
            file_extension=video_type, resolution=resolution
        ).first().default_filename
        video_name = video_name.replace(f".{video_type}", f"_{resolution}.{video_type}")
        yt_downloader2 = YouTube(url, on_progress_callback=progress.emit)
        progress.emit(3, 3, 3)
        filesize.emit(yt_downloader2.streams.filter(
            file_extension=video_type,
            resolution=resolution
        ).first().filesize)
        yt_downloader2.streams.filter(
            file_extension=video_type,
            resolution=resolution
        ).first().download(download_path, filename=video_name)
        return 0
    except Exception as err:
        print(f"Error downloading video: {err}\n{format_exc()}")
        return 1

class YoutubeDownloader(BaseWindow):
    ytd_toggle_signal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(True, parent)
        self._edit_mode = False
        self.workers = {}

        self.edit_button = self.findChild(YelButton)
        self.edit_button.setToolTip("New Downloader")

        self.ytd_toggle_signal.connect(self.toggle_ytd)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        self.layout.addStretch()

        self.toggle_edit_mode(False)
        self.animate = True

        self.adjustSize()

    def toggle_ytd(self) -> None:
        if self.isHidden():
            print(11)
            # self.setFixedSize(1, 1)
            self.show()
            self.activateWindow()
            self.adjustSize()
        else:
            print(22)
            self.hide()

    def toggle_edit_mode(self, mode: Optional[bool] = None) -> None:
        self._edit_mode = not self._edit_mode if mode is None else mode
        for ind, widget in enumerate(self.layout.parentWidget().findChildren(QWidget)):
            try:
                widget.setHidden(not self._edit_mode)
            except Exception:
                del self.workers[ind]

        QApplication.instance().processEvents()

    def on_edit_button_clicked(self, event) -> None:
        self.add_worker()
        QApplication.instance().processEvents()
        self.adjustSize()
        return super().on_edit_button_clicked(event)

    def add_worker(self) -> None:
        active_workers = [worker for worker in self.workers.values() if worker is not None]
        if len(active_workers) < 5:
            ind = len(self.workers) + 1
            worker = DownloaderWorker(parent=self, ind=ind)
            self.workers[ind] = worker
            self.layout.insertWidget(self.layout.count() - 1, worker)
        else:
            # Display a message box
            warning = BaseDialog(
                "Maximum number of youtube downloaders reached",
                parent=self
            )

            # remove reject button frm the dialog
            for widget in warning.findChildren(RedButton):
                widget.setHidden(True)

            warning.exec_()

class SettingsDialog(BaseDialog):
    def __init__(self, title: str = "Title", parent: QWidget | None = None,
                 available_videos: list = None) -> None:
        super().__init__(title, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.available_videos = available_videos
        self.download_path = None
        print(f"Available videos: {self.available_videos}")

        download_path_label = QLabel("Download path")
        self.download_path_edit = QPushButton("Select path")

        self.download_path_edit.clicked.connect(self.select_download_path)

        video_type_label = QLabel("Video type")
        self.video_type_combo = QComboBox()
        self.video_type_combo.addItems(list(available_videos))
        self.video_type_combo.setCurrentIndex(0)
        self.video_type_combo.currentIndexChanged.connect(self.update_resolution_combo)

        resolution_label = QLabel("Resolution")
        self.resolution_combo = QComboBox()

        # create a list with all values
        self.resolutions = []
        for res_list in self.available_videos.values():
            for res in res_list:
                if res is not None:
                    self.resolutions.append(res)

        self.resolutions = list(set(self.resolutions))
        self.resolution_combo.addItems(self.resolutions)
        self.resolution_combo.setCurrentIndex(0)
        self.resolution_combo.currentIndexChanged.connect(self.update_video_type_combo)

        self.layout.addWidget(download_path_label, 0, 0)
        self.layout.addWidget(self.download_path_edit, 0, 1)
        self.layout.addWidget(video_type_label, 1, 0)
        self.layout.addWidget(self.video_type_combo, 1, 1)
        self.layout.addWidget(resolution_label, 2, 0)
        self.layout.addWidget(self.resolution_combo, 2, 1)

    def update_resolution_combo(self, index) -> None:
        self.video_type_combo.setCurrentIndex(index)
        old_resolution = self.resolution_combo.currentText()
        self.resolution_combo.clear()
        self.resolution_combo.addItems(self.available_videos[self.video_type_combo.currentText()])
        if old_resolution in self.available_videos[self.video_type_combo.currentText()]:
            self.resolution_combo.setCurrentText(old_resolution)
        else:
            self.resolution_combo.setCurrentIndex(0)

    def update_video_type_combo(self) -> None:
        if self.resolution_combo.currentText() not in self.available_videos[self.video_type_combo.currentText()]:
            self.video_type_combo.setCurrentText("")

    def select_download_path(self) -> None:
        self.download_path = QFileDialog.getExistingDirectory(
            self,
            "Select download path",
            os.path.expanduser("~")
        )
        if self.download_path:
            self.download_path_edit.setText(f"..{os.path.sep}{self.download_path.split(os.path.sep)[-1]}")

    def get_settings(self) -> dict:
        return {
            "download_path": self.download_path,
            "video_type": self.video_type_combo.currentText(),
            "resolution": self.resolution_combo.currentText()
        }

class DownloaderWorker(QWidget):
    """DownloaderWorker class is used to create different instances of the youtube downloader widget.

    Args:
        QWidget (QWidget): QWidget
    """

    download_progress_signal = pyqtSignal(int, int, int)
    video_size_signal = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None, ind: int = 0):
        super().__init__()
        self.parent = parent
        self.ind = ind

        self.video_type = "mp4"
        self.video_resolution = "720p"
        self.video_url = ""
        self.video_location = ""
        self.video_name = ""

        # set minimum width
        self.setMinimumWidth(int(580 * UI_SCALE))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        self.video_size = 0

        self.download_progress_signal.connect(self.update_progress_bar)
        self.video_size_signal.connect(self.update_video_size)

        self.add_yt_widget = QWidget(self)
        self.layout.addWidget(self.add_yt_widget)

        self.add_yt_layout = QVBoxLayout()
        self.add_yt_widget.setLayout(self.add_yt_layout)

        self.top_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()
        self.progress_layout = QHBoxLayout()

        self.add_yt_layout.addLayout(self.top_layout)
        self.add_yt_layout.addLayout(self.bottom_layout)
        self.add_yt_layout.addLayout(self.progress_layout)

        yt_label = QLabel(f"Youtube Downloader {ind if ind > 0 else ''}")
        yt_label.setFont(get_font(size=int(16 * UI_SCALE)))
        yt_label.setStyleSheet("color: #282828")

        self.add_url_entry = Entry(self, place_holder="URL")
        # set minimum width
        self.add_url_entry.setMinimumWidth(int(430 * UI_SCALE))
        # set font size
        self.add_url_entry.setFont(get_font(size=int(11 * UI_SCALE)))

        self.add_download_button = GrnButton(self, "radial")
        self.add_settings_button = YelButton(self, "radial")
        self.add_delete_button = RedButton(self, "radial")
        self.add_download_button.setToolTip("Download")
        self.add_settings_button.setToolTip("Settings")
        self.add_delete_button.setToolTip("Delete")

        self.add_download_button.clicked.connect(self.download_video)

        self.add_delete_button.clicked.connect(self.delete_widget)

        self.add_settings_button.clicked.connect(self.show_settings_dialog)

        self.top_layout.addWidget(yt_label)

        self.bottom_layout.addWidget(self.add_url_entry)
        self.bottom_layout.addSpacing(int(5 * UI_SCALE))
        self.bottom_layout.addWidget(self.add_download_button)
        self.bottom_layout.addSpacing(int(5 * UI_SCALE))
        self.bottom_layout.addWidget(self.add_settings_button)
        self.bottom_layout.addSpacing(int(5 * UI_SCALE))
        self.bottom_layout.addWidget(self.add_delete_button)
        self.bottom_layout.addStretch()

        self.progress_bar = RoundedProgressBar(self)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(int(5 * UI_SCALE))

        self.progress_layout.addWidget(self.progress_bar)

    def download_video(self) -> None:
        if self.add_url_entry.text() and self.add_url_entry.text().startswith("https://www.youtube.com/watch?v="):
            self.video_url = self.add_url_entry.text()
        if self.video_url:
            download_youtube_video(
                self.video_url,
                download_path=self.video_location,
                video_type=self.video_type,
                resolution=self.video_resolution,
                progress=self.download_progress_signal,
                filesize=self.video_size_signal
            )
        else:
            self._show_warning("Please enter a valid URL")

    def update_progress_bar(self, chunk, file_handle, bytes_remaining):
        if self.video_size:
            percentage = int((1 - bytes_remaining / self.video_size) * 100)
        else:
            percentage = bytes_remaining
        print(f"Progress: {percentage}%")
        self.progress_bar.setValue(percentage)

    def update_video_size(self, size: int) -> None:
        self.video_size = size

    def delete_widget(self) -> None:
        self.parent.layout.removeWidget(self)
        self.deleteLater()

        length = len([worker for worker in self.parent.workers.values() if worker is not None])
        self.parent.setFixedHeight(int(self.height() * length * 1.05))

        self.parent.workers[self.ind] = None
        length = len([worker for worker in self.parent.workers.values() if worker is not None])
        if len([worker for worker in self.parent.workers.values() if worker is not None]) == 0:
            self.parent.toggle_edit_mode(False)
            self.parent.setFixedWidth(0)
            self.parent.setFixedHeight(0)
            self.parent.adjustSize()

    def _show_warning(self, msg: str) -> None:
        warning = BaseDialog(
            msg,
            parent=self
        )
        # remove reject button frm the dialog
        for widget in warning.findChildren(RedButton):
            widget.setHidden(True)

        warning.exec_()

    def show_settings_dialog(self) -> None:
        if not self.add_url_entry.text():
            self._show_warning("Please enter a valid URL first")
        else:
            available_videos = get_available_videos(self.add_url_entry.text())
            settings_dialog = SettingsDialog(
                title="Settings",
                available_videos=available_videos,
            )
            settings_dialog.exec_()

            settings = settings_dialog.get_settings()
            self.video_type = settings["video_type"]
            self.video_resolution = settings["resolution"]
            self.video_location = settings["download_path"]
            print(self.video_location)


window = YoutubeDownloader()

menu = AddOnBase.system_tray_icon.contextMenu()
action = menu.addAction("Youtube Downloader")
action.triggered.connect(window.ytd_toggle_signal.emit)

AddOnBase().set_activate_shortcut(QKeySequence("Ctrl+Shift+Y"))

AddOnBase().activate = window.ytd_toggle_signal.emit