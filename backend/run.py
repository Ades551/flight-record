from threading import Thread

from database import init_db
from flask_app import PORT, create_app
from threads.opensky import OpenSkyThread
from threads.spokendata import SpokenDataThread

if __name__ == "__main__":
    app = create_app()
    init_db()

    flask_app = Thread(
        target=app.run, kwargs={"debug": False, "host": "0.0.0.0", "port": PORT}
    )
    opensky = OpenSkyThread()
    spokendata = SpokenDataThread()

    # app.run(debug=True, host="0.0.0.0", port=PORT)
    flask_app.start()
    opensky.start()
    spokendata.start()

    flask_app.join()
    opensky.join()
    spokendata.join()
