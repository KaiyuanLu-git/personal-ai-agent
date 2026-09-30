import datetime

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculator(expression: str):
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return 'error: charactor not allowed'
        else:
            return str(eval(expression))
    except Exception as e:
        return f"error: {e}"