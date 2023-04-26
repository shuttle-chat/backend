# Copyright 2023 iiPython

# Modules
from blacksheep import Request, Application
from shuttle.helpers import resp_json

# Mounting handlers
def mount_api(app: Application, api_specs: dict) -> None:
    for api_version, endpoints in api_specs.items():
        for endpoint, data in endpoints.items():
            async def internal_callback(req: Request) -> dict:
                objects = await req.form()

                # Perform typechecking
                aspec = data["aspec"]
                for key, value in objects.items():
                    if key not in aspec.args:
                        return resp_json({
                            "code": 400,
                            "message": f"received unexpected object '{key}'"
                        })

                    try:
                        objects[key] = aspec.annotations[key](value)

                    except ValueError:
                        return resp_json({
                            "code": 400,
                            "message": f"object '{key}' must be of type '{aspec.annotations[key].__name__}'"
                        })

                defaults = aspec.args[-len(aspec.defaults):] if aspec.defaults is not None else []
                for obj in aspec.args:
                    if (obj not in objects) and (obj not in defaults):
                        return resp_json({"code": 400, "message": f"missing required argument '{obj}'"})

                # Main try-catch in case something goes wrong
                try:
                    return resp_json({"code": 200} | (data["cb"](**(objects)) or {}))

                except Exception as e:
                    print(f"Internal route error ({type(e).__name__}) on /api/{api_version}/{endpoint}:")
                    print(e)
                    return resp_json({"code": 500})

            add_method = getattr(app.router, f"add_{data['method']}")
            add_method(f"/api/{api_version}/{endpoint}", internal_callback)
