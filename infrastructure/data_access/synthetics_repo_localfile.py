import pickle

from domain.model import MeshResults
from domain.types import TestID


class SyntheticsRepoLocalFile:
    """
    SyntheticsRepoLocalFile implements domain.Repo protocol.
    It allows to load/store MeshResults to a file.
    """

    def __init__(self, mesh_test_results_filename: str) -> None:
        self._mesh_test_results_filename = mesh_test_results_filename

    def get_mesh_test_results(self, TestID, int) -> MeshResults:
        try:
            return self.load(self._mesh_test_results_filename)
        except Exception as err:
            raise Exception(f'Failed to unpickle mesh test results from "{self._mesh_test_results_filename}"') from err

    @staticmethod
    def store(obj: MeshResults, filename: str) -> None:
        with open(filename, "wb") as f:
            pickle.dump(obj, f)

    @staticmethod
    def load(filename: str) -> MeshResults:
        with open(filename, "rb") as f:
            return pickle.load(f)
