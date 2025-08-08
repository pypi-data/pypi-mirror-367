from nbformat import NotebookNode

from . import Operation


class CheckCell(Operation):
    def __call__(self, cell: NotebookNode) -> NotebookNode:
        self.check_cell(cell)
        return cell

    def check_cell(self, cell: NotebookNode) -> None:
        raise NotImplementedError
