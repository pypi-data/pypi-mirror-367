"""QPU and QpusByAlias classes for qciconnect package."""
from pydantic import ValidationError as PydanticValidationError
from tabulate import tabulate
from typeguard import typechecked

from qciconnect.exceptions import QciConnectClientError

from .client import BackendJob, QciConnectClient
from .result_handling import BackendResult, FutureBackendResult


class Qpu:
    """Class representing a quantum circuit processing unit (real device or simulator)."""

    def __init__(
        self,
        identifier: int,
        name: str,
        manufacturer: str,
        qubit_count: int,
        status: str,
        client: QciConnectClient,
    ):
        """Constructs a Qpu object.

        Args:
            identifier: Unique identifier of the quantum circuit processing unit.
            name: Name of the quantum circuit processing unit.
            manufacturer: Manufacturer of the quantum circuit processing unit.
            qubit_count: Number of qubits available on the QPU.
            status: Current operational status.
            client: Instance of QciConnectClient - QCI Connect RestAPI client.
        """
        self._id = identifier
        self._name = name
        self._alias = name.lower().replace(" ", "_").replace("-", "_")
        self._manufacturer = manufacturer
        self._qubit_count = qubit_count
        self._status = status
        self._client = client

    @typechecked
    def submit(
        self,
        circuit: str,
        primitive: str,
        shots: int = 10000,
        wait_for_results: bool = True,
        name: str = "Hequate QPU Job",
        comment: str = "Issued via API",
        qpu_options: dict | None = None,
    ) -> FutureBackendResult | BackendResult | None:
        """Submits the circuit to the QPU for execution according to primitive and shots.

        Args:
            name: Name of the job.
            circuit: Quantum circuit to be executed.
            primitive: Way of execution.
            shots: Number of runs/executions.
            wait_for_results: wait for the backend to finished the submitted job.
            comment: Optional string to further describe the job
            qpu_options: Additional options for the QPU.

        Returns: BackendResult, which is measurement data with a bunch of meta data or
                 FutureBackendResult which is a promise to later return a BackendResult
        """
        if qpu_options is None:
            qpu_options = {}
        try:
            job = BackendJob(
                self._id,
                circuit,
                primitive,
                name=name,
                shots=shots,
                comment=comment,
                qpu_options=qpu_options
            )
        except (PydanticValidationError, ValueError) as e:
            print(e)
            return None

        if wait_for_results:
            try:
                result = self._client.submit_backend_job_and_wait(job)
                if result.last_qpu_result is None:
                    print("Job failed(?) - no result data available.")
                    return None
            except (QciConnectClientError, PydanticValidationError) as e:
                print(e)
                return None
            return BackendResult.from_qpu_task_result(result.last_qpu_result)
        else:
            try:
                job_id = self._client.submit_backend_job(job)
            except (QciConnectClientError, PydanticValidationError) as e:
                print(e)
                return None
            return FutureBackendResult(job_id, self._client)

    def __str__(self) -> str:
        """Returns a string representation of the QPU with its alias, qubit count, and status."""
        return f"Name: {self._alias}, #Qubits: {self._qubit_count}, Status: {self._status}"

    def get_qpu_info(self) -> list[str]:
        """Returns list containing QPU alias, #qubits, and status."""
        return [self._alias, str(self._qubit_count), self._status]

    def __dir__(self):
        """Returns a list of attributes and methods of the specific Qpu  (w/o dunders)."""
        method_list = []
        for attr in dir(self):
            if not attr.startswith("__"):
                method_list.append(attr)
        return method_list


class QpuByAlias:
    """Dictionary of available QPUs on the platform indexed by their aliases."""

    def __init__(self, client: QciConnectClient):
        """Constructs a dict of QPUs available on the platform (indexed by their aliases).

        Args:
            qpu_list: list of QPUTable objects.
            client: Instance of QciConnectClient - QCI Connect RestAPI client.
        """
        self._client = client
        self._update_qpu_dict()

    def _update_qpu_dict(self):
        qpu_list = self._client.get_available_qpus()
        self._qpus = {}
        for qpu_entry in qpu_list:
            qpu = Qpu(
                qpu_entry["qpu_id"],
                qpu_entry["name"],
                qpu_entry["manufacturer"],
                qpu_entry["number_of_qubits_available"],
                qpu_entry["status"],
                self._client,
            )
            self._qpus[qpu._alias] = qpu

    def __getattr__(self, name) -> Qpu | None:
        """Returns a Qpu object if it exists, otherwise None."""
        try:
            return self._qpus.__getitem__(name)
        except KeyError as e:
            print(e)
            return None

    def __dir__(self):
        """Returns a list of QPUs and other attributes."""
        extended_key_list = list(self._qpus.keys()) + list(super().__dir__())
        return extended_key_list

    def show(self):
        """Prints table of available QPUs including their qubit counts and status."""
        self._update_qpu_dict()
        all_qpu_info = []
        for qpu in self._qpus.values():
            all_qpu_info.append(qpu.get_qpu_info())

        print(tabulate(all_qpu_info, headers=["Alias", "Qubits", "Status"]))
