from typing import Callable, Union, TypeAlias

Serializable: TypeAlias = Union[
    bool, str, None,
    list["Serializable"], tuple["Serializable", ...], dict["Serializable", "Serializable"]]
SerializableCallable: TypeAlias = Callable[..., Serializable]
