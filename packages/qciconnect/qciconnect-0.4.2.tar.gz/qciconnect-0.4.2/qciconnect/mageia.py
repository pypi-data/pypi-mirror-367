"""Provides a class for interacting with the "QCI Connect" quantum computing platform."""
from typeguard import typechecked

from .client import QciConnectClient
from .exceptions import KeycloakTokenManagerError, QciConnectClientError, ResultError
from .methods import Methods
from .qpus import QpuByAlias
from .result_handling import Results


class Mageia:
    """Represents a frontend to a quantum computing platform.

    Attributes:
        methods: Collects and provides all the methods/compiler passes available on the platform.
        qpus: Collects and provides all the quantum processing units (including simulators)
              available on the platform.
    """

    _DEFAULT_SERVER = "https://qc-plat-pro.dlr.de/"
    _LOCALHOST = "http://127.0.0.1:8000/"

    @typechecked
    def __init__(
        self, username: str | None = None, password: str | None = None, server: str | None = None
    ):
        """Constructs a Mageia/Client object."""
        if (username is None or password is None) and server is None:
            print(f"Warning! No server and no credentials given.\n"
                  f"In order to use the QCI Connect server {self._DEFAULT_SERVER} "
                  f"you need to provide username and password.\n"
                  f"Falling back to {self._LOCALHOST} as server.")
            server = self._LOCALHOST
        if username is not None and password is not None and server is None:
            server = self._DEFAULT_SERVER

        try:
            self._client = QciConnectClient(server, username, password)
            if server == self._DEFAULT_SERVER:
                self._update_tac_and_privacy_status()
                if not self.tacs_accepted:
                    print(
                        f"Terms and conditions not accepted. Please accept them on "
                        f"{self._DEFAULT_SERVER}."
                    )
                if not self.privacy_notice_accepted:
                    print(
                        f"Privacy notice not accepted. Please accept the privacy notice on "
                        f"{self._DEFAULT_SERVER} using a web browser."
                    )

            self._update_methods()
            self._update_qpus()
            self._update_results()
        except (KeycloakTokenManagerError, QciConnectClientError, ResultError) as e:
            print(e)
        except Exception as e:  # noqa: BLE001
            if (
                server.__contains__("localhost")
                or server.__contains__("0.0.0.0")
                or server.__contains__("127.0.0.1")
            ):
                print(
                    "Please run `docker compose up` before connecting to your backend. \n"
                    "For further information see also https://gitlab.dlr.de/qci-connect/partners/all/qciconnect-sdk"
                )
            else:
                print(f"Connection to {server} could not be established.")
                print(e, type(e))

    @property
    def server_address(self) -> str:
        """Returns URL of the platform."""
        return self._client.server_address

    @server_address.setter
    def server_address(self, value: str):
        """Sets the URL of the platform and retrieves available methods and QPUs.

        Args:
            value: URL of the platform that shall be used.
        """
        self._client.server_address = value
        self._update_methods()
        self._update_qpus()
        self._update_results()

    def _update_methods(self):
        """Updates the methods/compiler passes available on the platform."""
        compiler_list = self._client.get_available_compilers()
        self.methods = Methods(compiler_list, self._client)

    def _update_qpus(self):
        """Updates the quantum processing units available on the platform."""
        self.qpus = QpuByAlias(self._client)

    def _update_results(self):
        """Updates the results of the jobs available on the platform."""
        self.results = Results(self._client)
        self.results.refresh()

    def _update_tac_and_privacy_status(self):
        """Updates the terms and conditions and privacy notice status of the platform."""
        self.tacs_accepted = self._client.get_tac_status()
        self.privacy_notice_accepted = self._client.get_privacy_notice_status()
