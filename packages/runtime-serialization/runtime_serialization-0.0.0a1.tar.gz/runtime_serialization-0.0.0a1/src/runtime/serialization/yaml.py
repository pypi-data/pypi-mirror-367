try:
    import yaml as _
except ModuleNotFoundError: # pragma: no cover
    raise ModuleNotFoundError("Package PyYAML is required, to use runtime.serialization.yaml namespace")

from runtime.serialization.core.formats.yaml.serializer import YamlSerializer as Serializer, serialize, deserialize

__all__ = [
    'Serializer',
    'serialize',
    'deserialize'
]