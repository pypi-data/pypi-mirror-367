from yapp.result import Result


class Dummy:
    def name() -> Result[str]
        return Ok("Hello, World!")



def func2() -> Result[str]
    dummy = Dummy()
    name = dummy.name()
    if not name:
        return Result.error(f"Failed to get name: {name.as_error}")
