from typing import Optional, List, Callable
from fastapi.types import DecoratedCallable


class BluePrint(object):
    def __init__(self, name):
        self.name = name
        self.mound = []

    def route(
        self,
        path: str,
        **options
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.mound.append((func, path, options))
            return func

        return decorator

    def register(self, ar, url_prefix=None):
        """
        把红图注册到蓝图上
        :param ar: APIRouter 对象
        :param url_prefix:
        :return:
        """
        if url_prefix is None:
            url_prefix = '/' + self.name
        for f, path, options in self.mound:
            # print(options, f.__name__)
            # endpoint = options.pop("endpoint", f.__name__)
            methods = options.pop("methods", None)
            ar.add_api_route(url_prefix+path, f, methods=methods)
