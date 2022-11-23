def wait_f(message):
    if json.loads(message.value()) % 5 == 0:
        return "hi"