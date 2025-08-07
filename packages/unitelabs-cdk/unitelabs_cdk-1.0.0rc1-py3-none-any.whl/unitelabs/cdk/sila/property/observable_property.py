import collections.abc
import inspect
import warnings

import typing_extensions as typing

import sila
from sila.server import Native, SiLAError, UndefinedExecutionError
from unitelabs.cdk.subscriptions import Subscription

from .. import utils
from ..common import Decorator
from ..common.errors import define_error
from ..data_types import infer, to_sila
from ..metadata import Metadatum

if typing.TYPE_CHECKING:
    from ..common import Feature

T = typing.TypeVar("T")
Stream = collections.abc.AsyncIterator[T]


class ObservableProperty(Decorator):
    """A property describes certain aspects of a SiLA server that do not require an action on the SiLA server."""

    @typing.override
    def attach(self, feature: "Feature") -> bool:
        if not super().attach(feature):
            return False

        self._name = self._name or utils.humanize(self._function.__name__.removeprefix("subscribe_"))
        self._identifier = self._identifier or self._name.replace(" ", "")
        self._description = inspect.getdoc(self._function) or ""

        type_hint = return_annotation = inspect.signature(self._function).return_annotation
        if type_hint is inspect._empty:
            type_hint = Stream[Native]

        type_hint = typing.get_args(type_hint)

        if not type_hint:
            output = return_annotation.__name__ if hasattr(return_annotation, "__name__") else return_annotation
            warnings.warn(
                f"Invalid return type for observable property '{self._identifier}'"
                f": expected `sila.Stream[...]`, received `{output}`.'",
                stacklevel=2,
            )
            type_hint = (return_annotation,)

        data_type = infer(type_hint[0], feature)

        self._responses = {
            self._identifier: sila.Element(identifier=self._identifier, display_name=self._name, data_type=data_type)
        }

        self._handler = sila.server.ObservableProperty(
            identifier=self._identifier,
            display_name=self._name,
            description=self._description,
            function=self.execute,
            errors={Error.identifier: Error for error in self._errors if (Error := define_error(error))},
            data_type=data_type,
            feature=feature,
        )
        self._metadata = Metadatum._infer_metadata(self)

        return True

    @typing.override
    async def execute(
        self, metadata: dict[sila.MetadataIdentifier, Native], **parameters
    ) -> collections.abc.AsyncIterator[Native]:
        if not self._feature:
            raise RuntimeError

        try:
            function = self._with_metadata(self._function, metadata)
            function = self._with_parameters(function, parameters)

            responses = self._execute(function)

            async for item in responses:
                yield to_sila(item, sila.Structure.create(self._responses), self._feature)
        except SiLAError:
            raise
        except Exception as error:
            if type(error) in self._errors:
                raise define_error(error)(str(error)) from None

            msg = f"{error.__class__.__name__}: {error}"
            raise UndefinedExecutionError(msg) from error

    @typing.override
    async def _execute(self, function: collections.abc.Callable) -> collections.abc.AsyncIterator[Native]:
        responses = function()

        if inspect.iscoroutine(responses):
            responses = await responses

        if isinstance(responses, Subscription):
            async for response in responses:
                yield {self._identifier: response}

            responses.terminate()

        elif inspect.isasyncgen(responses):
            async for response in responses:
                yield {self._identifier: response}

        elif inspect.isgenerator(responses):
            for response in responses:
                yield {self._identifier: response}
