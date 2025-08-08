from nbformat import NotebookNode

from jpconvert.operations import CheckCell


class FailIfOutputIsEmbedded(CheckCell):
    def check_cell(self, cell: NotebookNode) -> None:
        if cell['cell_type'] == 'code':
            if 'execution_count' in cell and cell['execution_count'] is not None:
                raise OutputEmbeddedError(f'execution count is set for cell {cell["id"]}')
            if 'outputs' in cell and len(cell['outputs']) > 0:
                raise OutputEmbeddedError(f'output is embedded for cell {cell["id"]}')


class OutputEmbeddedError(Exception):
    pass
