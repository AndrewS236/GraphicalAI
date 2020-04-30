from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
# from PyQt5.QtGui import QLine

from src.debug import *
from src.components.workspace.nodes import Nodes

from typing import List, Dict, Optional
import os


class NodeMenu(QTreeWidget):
	START_POS = [500, 200]
	DIFF = (30, 10)  # move in what direction
	MAX_DIFF = 5  # maximum amount of times before reset the counter

	def __init__(self, view: QGraphicsView, menu_data: Dict[str, List[Nodes]], parent=None):
		super().__init__(parent=parent)
		self.view = view
		self.inst_pos = NodeMenu.START_POS.copy()  # node instantiate position
		self.counter = 0  # counting for # of times the user added the node; for the diff. node pos

		self.nodes = {}  # node title to node class reference mapping
		self.items: List[QTreeWidgetItem] = []
		for cat in menu_data:
			self.items.append(QTreeWidgetItem(self, [cat]))
			self.items[-1].addChildren([
				QTreeWidgetItem([nds.title])
				for nds in menu_data[cat]
			])
			for nds in menu_data[cat]: self.nodes[nds.title] = nds

		self.setHeaderHidden(True)
		self.addTopLevelItems(self.items)

		self.itemActivated.connect( lambda itm, col: self.addModel(self.nodes.get(itm.text(col))) )

	def addModel(self, nd_cls: Optional[Nodes]):
		# there should only be one model that have a unique name thus it should have only one item in the list
		# and each item in the list must be model class meaning it has the method create()

		if nd_cls is not None:
			self.view.scene().addItem(nd_cls.create(self.view, self.inst_pos))

			if self.counter > self.MAX_DIFF:
				print(NodeMenu.START_POS)
				self.inst_pos = NodeMenu.START_POS.copy()
				self.counter = 0
			self.inst_pos[0] += self.DIFF[0]
			self.inst_pos[1] += self.DIFF[1]
			self.counter += 1


class ProjectRootEdit(QPushButton):
	def __init__(self, start=os.path.expanduser("~")):
		super().__init__()
		self.dir = ""
		self.lastText = start  # starting directory; start with the *start* directory

		self.setText(start)

		self.clicked.connect(lambda checked: self.onClick())

	def onClick(self):
		""" creates the file dialogue """
		self.wind = QMainWindow()
		self.wind.setWindowTitle("File Dialogue")
		self.wind.setGeometry(0, 0, 1000, 400)

		self.file_dialog = QFileDialog()
		self.file_dialog.setFileMode(self.file_dialog.DirectoryOnly)
		self.file_dialog.setViewMode(self.file_dialog.List)

		self.file_dialog.fileSelected.connect(lambda dir: self.set_dir(dir))
		self.file_dialog.finished.connect(lambda code: self.finished(code))

		self.wind.setMenuWidget(self.file_dialog)
		self.wind.show()

	def set_dir(self, url):
		self.dir = url+"/"
		self.setText(self.dir)
		self.wind.close()  # closes the window\

	def finished(self, code: int):
		print("---", code)
		self.wind.close()


class InputDialog(QPushButton):
	inputSelected = pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.txt = ""

		self.clicked.connect(lambda checked: self.on_click())

	def on_click(self):
		self.wind = QMainWindow()
		self.wind.setWindowTitle("Input Dialogue")
		self.wind.setGeometry(200, 300, 300, 100)  # todo: GLOBAL POSITION; may not position it correctly
		self.wind.setWindowModality(Qt.ApplicationModal)

		self.inp_dialog = QInputDialog()
		self.inp_dialog.setLabelText("Input your model's name: ")

		self.inp_dialog.textValueSelected.connect(lambda txt: self.set_txt(txt))
		self.inp_dialog.finished.connect(lambda code: self.wind.close())

		self.wind.setMenuWidget(self.inp_dialog)
		self.wind.show()

	def set_txt(self, s: str):
		self.txt = s
		self.inputSelected.emit(s)


class NewProject(QPushButton):  # todo: a mess of code; revisit for some aesthetic & maintenance issue
	inputSelected = pyqtSignal(str, str)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = ""
		self.dir: str = ""

		self.clicked.connect(lambda checked: self.on_click())

	def on_click(self):
		self.wind = QMainWindow(parent=self)
		self.wind.setWindowTitle("Select Directory")

		pos: QPoint = self.wind.mapToGlobal(QPoint(100, 300))
		self.wind.setGeometry(pos.x(), pos.y(), 300, 100)  # todo: GLOBAL POSITION; may not position it correctly

		self.wind.setWindowModality(Qt.WindowModal)

		def row(widget_a, widget_b):
			section = QHBoxLayout()
			section.addWidget(widget_a)
			section.addWidget(widget_b)
			return section

		self.inp_dialog = QDialog()

		b_ok = QPushButton("OK")
		b_ok.clicked.connect(lambda checked: self.inp_dialog.accept())

		result = QHBoxLayout()
		result.addStretch()
		result.addWidget(b_ok)

		prj_edit = QLineEdit()
		prj_dir = ProjectRootEdit()

		central = QVBoxLayout()
		central.addLayout(row(QLabel("Project Name: "), prj_edit))
		central.addWidget(prj_dir)
		central.addLayout(result)

		self.inp_dialog.accepted.connect(lambda: self.set_txt(prj_edit.text(), prj_dir.dir))
		self.inp_dialog.setLayout(central)

		self.wind.setMenuWidget(self.inp_dialog)
		self.wind.show()

	def set_txt(self, name: str, dir: str):
		self.wind.close()
		self.name = name
		self.dir = dir

		if name == "" or dir == "": print("Error: Some values have not been selected yet")
		else: self.inputSelected.emit(name, dir)


class LoadProject(QPushButton):
	inputSelected = pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.dir = ""

		self.clicked.connect(lambda checked: self.on_click())

	def on_click(self):
		self.wind = QMainWindow()
		self.wind.setWindowTitle("File Dialogue")
		self.wind.setGeometry(200, 300, 1000, 400)  # todo: GLOBAL POSITION; may not position it correctly
		self.wind.setWindowModality(Qt.ApplicationModal)

		self.fl_dlg = QFileDialog()
		self.fl_dlg.fileSelected.connect(lambda s: self.set_txt(s))
		self.fl_dlg.finished.connect(lambda code: self.wind.close())

		self.wind.setMenuWidget(self.fl_dlg)
		self.wind.show()

	def set_txt(self, dir: str):
		self.dir = dir
		self.inputSelected.emit(dir)
		self.wind.close()


#https://stackoverflow.com/questions/5671354/how-to-programmatically-make-a-horizontal-line-in-qt
class QHLine(QFrame):
	def __init__(self, visible=True):
		super().__init__()
		self.setFrameShape(QFrame.HLine)
		if not visible: self.setLineWidth(-1)
		self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
	def __init__(self, visible=True):
		super().__init__()
		self.setFrameShape(QFrame.VLine)
		if not visible: self.setLineWidth(-1)
		self.setFrameShadow(QFrame.Sunken)


class ErrorBox(QMessageBox):
	# once the error is created, it can not be removed from the list unless it was removed before a commit
	E000 = {"code": "E000", "level": QMessageBox.Information, "title": "No Title", "txt": "No Text"}
	E001 = {"code": "E001", "level": QMessageBox.Critical, "title": "Project", "txt": "The project directory has not been set."}
	E002 = {"code": "E002", "level": QMessageBox.Warning, "title": "Project", "txt": "Invalid project file"}
	E003 = {"code": "E003", "level": QMessageBox.Warning, "title": "Project", "txt": "Invalid project directory"}
	E004 = {"code": "E004", "level": QMessageBox.Warning, "title": "Project", "txt": "Invalid project key\n(You have not set the model name)"}
	E005 = {"code": "E005", "level": QMessageBox.Critical, "title": "Executor", "txt": "Runtime Error"}
	E006 = {"code": "E006", "level": QMessageBox.Critical, "title": "Project", "txt": "Executor file failed to load"}
	E007 = {"code": "E007", "level": QMessageBox.Critical, "title": "Project", "txt": "Model file failed to load"}

	def __init__(self, code="E000", title="No Title", level=QMessageBox.Information, txt="No Text"):
		super().__init__()
		self.setIcon(level)
		self.setText(txt)
		self.setWindowTitle(code+" - "+title)


class ModelWorkspaceSelector(QComboBox):
	def __init__(self, items: list, parent=None):
		super().__init__(parent)
		self.items = items

		# self.textActivated.connect(lambda s: self.selected_workspace(s))
		# self.currentIndexChanged.connect(lambda ind: self.selection_chng(ind))

		self.update_list(items)

	def update_list(self, items):
		txt = self.currentText()
		self.clear()
		self.items = items
		[self.addItem("<undefined>" if c.name is "" else c.name) for c in items]
		if txt in [i.name for i in items]:
			self.setCurrentText(txt)

	def retrieve_name(self):
		return self.items[self.currentIndex()]


if __name__ == '__main__':
    pass
