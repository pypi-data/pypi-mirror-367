import sys
from .env import ENV


def say_hello_to_user(username: str) -> str:
    """Say hello to the user with environment information."""
    user_stdio_args = sys.argv[1:]  # Skip script name
    
    return f"""Hello, {username}!

Your request country: [{ENV.get("USER_REQUEST_COUNTRY")}]

Your function region: [{ENV.get("SERVERLESS_FUNCTION_REGION")}]

Your sample env var: [{ENV.get("SAMPLE_ENV")}]

Your stdio args: [{", ".join(user_stdio_args)}]"""