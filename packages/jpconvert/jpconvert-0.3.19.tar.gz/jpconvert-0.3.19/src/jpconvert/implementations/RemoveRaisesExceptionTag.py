from nbformat import NotebookNode

from ..operations import MapCell


class RemoveRaisesExceptionTag(MapCell):
    def map_cell(self, cell: NotebookNode) -> NotebookNode:
        if 'metadata' in cell and 'tags' in cell['metadata']:
            if 'jp-remove-raises-exception' in cell['metadata']['tags']:
                cell['metadata']['tags'] = [t
                                            for t in cell['metadata']['tags']
                                            if t != 'raises-exception']

        return cell
