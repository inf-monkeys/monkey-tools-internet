from src.server.app import app
from src.services import *
from src.config import config_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config_data.get("server", {}).get("port", 5000))
