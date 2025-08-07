from __future__ import annotations

import importlib.util
import sys


def make_getattr(package_name: str):
    def __getattr__(name: str):
        """Defer importing own modules until attempting to access an attribute.

        Importing this in ``__init__`` will overwrite relative imports.
        """
        fullname = package_name + '.' + name

        try:
            return sys.modules[fullname]
        except KeyError:
            spec = importlib.util.find_spec(fullname)
            if spec is None or spec.loader is None:
                # ``AttributeError`` is converted to an ``ImportError`` by the import machinery.
                raise AttributeError from None

            spec.loader = loader = importlib.util.LazyLoader(spec.loader)
            sys.modules[fullname] = module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)

            return module

    return __getattr__
