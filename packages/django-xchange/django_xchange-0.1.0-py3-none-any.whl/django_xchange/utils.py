import importlib


def resolve_fqn(klass: str) -> object:
    module_path, class_name = klass.rsplit('.', 1)

    module = importlib.import_module(module_path)
    return getattr(module, class_name)
