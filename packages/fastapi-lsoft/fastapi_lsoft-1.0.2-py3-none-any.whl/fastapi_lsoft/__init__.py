import functools

from starlette.responses import JSONResponse, Response
from pydantic import BaseModel

def cache_control(max_age: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            ret = await func(*args, **kwargs)
            if not isinstance(ret, Response):
                if isinstance(ret, BaseModel):
                    ret = ret.model_dump()
                response = JSONResponse(ret)
            else:
                response = ret

            cache_control_list = []
            if max_age is not None:
                cache_control_list.append(f"max-age={max_age}")

            if len(cache_control_list) > 0:
                cache_control_string = ",".join(cache_control_list)
                response.headers["Cache-Control"] = cache_control_string
            return response

        return inner

    return decorator
