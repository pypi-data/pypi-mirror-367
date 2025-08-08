try:
    import toml as _
except ModuleNotFoundError: # pragma: no cover
    raise ModuleNotFoundError("Package toml is required, to use runtime.serialization.toml namespace")

from runtime.serialization.core.formats.toml.serializer import TomlSerializer as Serializer, serialize, deserialize

__all__ = [
    'Serializer',
    'serialize',
    'deserialize'
]