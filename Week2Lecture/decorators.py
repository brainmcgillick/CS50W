def announce(f):
    def wrapper():
        print("About to run the function...")
        f()
        print("Function has been run.")
    return wrapper

@announce
def hello():
    print("Hello, world!")

hello()