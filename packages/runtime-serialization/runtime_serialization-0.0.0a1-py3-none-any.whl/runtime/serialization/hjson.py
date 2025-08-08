try:
    import hjson as _
except ModuleNotFoundError: # pragma: no cover
    raise ModuleNotFoundError("Package hjson is required, to use runtime.serialization.hjson namespace")

from runtime.serialization.core.formats.hjson.serializer import HjsonSerializer as Serializer, serialize, deserialize

__all__ = [
    'Serializer',
    'serialize',
    'deserialize'
]