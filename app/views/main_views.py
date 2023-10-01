from flask import Blueprint, url_for, current_app, render_template
from werkzeug.utils import redirect
import socket


bp = Blueprint("main", __name__, url_prefix="/")


# Load balancing test page routing functions
@bp.route("/loadbalancingtest")
def LBTest():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    ip = s.getsockname()[0]
    s.close()

    return "<h1>FROM " + ip + "</h1>"


# 메인 페이지 라우팅 함수
@bp.route("/")
def index():
    current_app.logger.info("Logging level: INFO")

    return render_template("index.html")
