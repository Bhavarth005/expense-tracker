from app import app

if __name__ == "__main":
    try:
        app.run()
    except e:
        log_file = open("expense-tracker.log", "a")
        log_file.write("\n")
        log_file.write(str(e))
