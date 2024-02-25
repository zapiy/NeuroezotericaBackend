import asyncio


def wrap_middleware(middleware):
    def wraps(func):
        if asyncio.iscoroutinefunction(middleware):
            async def inner(request, *args, **kwargs):
                return await middleware(request, lambda: func(request, *args, **kwargs))
            return inner
        else:
            def inner(request, *args, **kwargs):
                return middleware(request, lambda: func(request, *args, **kwargs))
            return inner
    return wraps
