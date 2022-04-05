import pathlib

################### DB vars ##################

postgres_host = "127.0.0.1"
postgres_user = "admin"
postgres_pass = "password"

################### Browser vars ##################

driver_path = str(pathlib.Path(__file__) / "drivers" / "chromedriver.exe")
