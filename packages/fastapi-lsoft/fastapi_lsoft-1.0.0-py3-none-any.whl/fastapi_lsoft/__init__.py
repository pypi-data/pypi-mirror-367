import functools

from starlette.responses import JSONResponse, Response


def cache_control(max_age: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            response = await func(*args, **kwargs)
            if not isinstance(response, Response):
                response = JSONResponse(response)

            cache_control_list = []
            if max_age is not None:
                cache_control_list.append(f"max-age={max_age}")

            if len(cache_control_list) > 0:
                cache_control_string = ",".join(cache_control_list)
                response.headers["Cache-Control"] = cache_control_string
            return response

        return inner

    return decorator
