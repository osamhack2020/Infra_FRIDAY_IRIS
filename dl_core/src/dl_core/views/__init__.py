from dl_core.views.weather import weather
from dl_core.views.holiday import holiday
from dl_core.views.predict import predict

def register_api(app):
    app.register_blueprint(weather)
    app.register_blueprint(holiday)
    app.register_blueprint(predict)