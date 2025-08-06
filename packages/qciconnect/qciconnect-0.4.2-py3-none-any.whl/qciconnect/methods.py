"""Methods module for qciconnect package. Contains the Method(s) class and related utilities."""
from typeguard import typechecked

from .client import CompilerJob, QciConnectClient
from .exceptions import InvalidIdentifierError, KeycloakTokenManagerError, QciConnectClientError
from .result_handling import CompilerResult, FutureCompilerResult


class Method:
    """Callable object representing a compiler pass."""

    def __init__(
        self, pass_name: str, compiler_id: int, compiler_name: str, client: QciConnectClient
    ):
        """Constructs a callable Method object, which submits a job to respective compile pass.

        Args:
            pass_name: Name of the compiler pass.
            compiler_id: ID of the compiler the compiler pass belongs to.
            compiler_name: Name of the compiler.
            client: Instance of QciConnectClient - QCI Connect RestAPI client.
        """
        self._pass_name = pass_name
        self._compiler_id = compiler_id
        self._compiler_name = compiler_name
        self._compiler_alias = compiler_name.lower().replace(" ", "_").replace("-", "_")
        if not self._compiler_alias.isidentifier():
            raise InvalidIdentifierError(
                f"Compiler alias {self._compiler_alias} is not a valid python identifier."
            )
        self._client = client

    @typechecked
    def __call__(
        self,
        input_circuits: dict[str, str],
        options: dict | None = None,
        wait_for_results: bool = True
    ) -> CompilerResult | FutureCompilerResult | None:
        """Submits input circuits to respective compile pass.

        Args:
            input_circuits: dict of input circuits.
            options: Options determining how to compile.
            wait_for_results: Wait for the computation and return result.
                              Otherwise, return only job ID.

        Returns: If wait_for_results == True, it returns the compilation Result,
                 which is the compiled circuits together with a bunch of meta data.
                 Otherwise, it returns FutureCompilerResult, which promises to return
                  the compilation result when it's available.
        """
        if options is None:
            options = {}

        compiler_job = CompilerJob(self._compiler_id, self._pass_name, options, input_circuits)
        try:
            if wait_for_results:
                result = self._client.submit_compiler_job_and_wait(compiler_job)
                return CompilerResult.from_compiler_task_result(result.last_compiler_result)
            else:
                job_id = self._client.submit_compiler_job(compiler_job)
                return FutureCompilerResult(job_id, self._client)
        except (QciConnectClientError, KeycloakTokenManagerError) as e:
            print(e)
            return None
        except Exception:
            raise

    def __str__(self) -> str:
        """Returns the compiler pass name together with the compiler alias."""
        return f"{self.pass_alias}_{self._compiler_alias}"

    @property
    def pass_alias(self):
        """Returns method/compiler pass alias."""
        return self._pass_name.lower().replace(" ", "_").replace("-", "_")


class Methods:
    """Provides a method/callable object for each compiler pass available on the platform."""

    def __init__(self, compiler_list: list, client: QciConnectClient):
        """Constructs an object containing all Method objects that are supported by the platform.

        This object is constructed by passing a list of compilers and a QciConnectClient.

        Args:
            compiler_list: list of CompilerTable objects.
            client: Instance of QciConnectClient - QCI Connect RestAPI client.
        """
        self._passes = {}
        for compiler in compiler_list:
            for pass_name in compiler["passes_available"]:
                try:
                    method = Method(pass_name, compiler["compiler_id"], compiler["name"], client)
                except InvalidIdentifierError as e:
                    print(e)
                full_pass_name = f"{method.pass_alias}_{method._compiler_alias}"

                if full_pass_name in self._passes:
                    raise InvalidIdentifierError(
                        f"Compiler pass {full_pass_name} already exists."
                    )

                self._passes[full_pass_name] = method

    def __getattr__(self, name) -> Method:
        """Retrieves a compiler pass by name. Raises a KeyError if the pass does not exist."""
        return self._passes.__getitem__(name)

    def __dir__(self):
        """Lists available compiler passes and other attributes/methods."""
        extended_key_list = list(self._passes.keys()) + super().__dir__()
        return extended_key_list

    def show(self):
        """Prints available compiler passes."""
        for method in self._passes.values():
            print(method)
