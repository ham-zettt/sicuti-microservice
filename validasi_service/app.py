from flask import Flask, jsonify, request, render_template, redirect, url_for
from models import db, LeaveRequest
import jwt
from functools import wraps

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@db/sicuti'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")  # Ambil token dari cookie
        print(token)
        if not token:
            return redirect(
                "http://localhost:5003/"
            )  # Redirect ke login jika token tidak ada
        try:
            decoded_token = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            request.user_id = decoded_token["user_id"]
            request.role = decoded_token["role"]
        except jwt.ExpiredSignatureError:
            return redirect(
                "http://localhost:5003/"
            )  # Redirect ke login jika token kadaluarsa
        except jwt.InvalidTokenError:
            return redirect(
                "http://localhost:5003/"
            )  # Redirect ke login jika token tidak valid
        return f(*args, **kwargs)

    return decorated


@app.route('/approve/<int:id>', methods=['PUT'])
def approve_leave(id):
    leave_request = LeaveRequest.query.get_or_404(id)
    leave_request.status = 'Approved'
    db.session.commit()
    return jsonify({"message": "Leave request approved!"})

@app.route('/reject/<int:id>', methods=['PUT'])
def reject_leave(id):
    leave_request = LeaveRequest.query.get_or_404(id)
    leave_request.status = 'Rejected'
    db.session.commit()
    return jsonify({"message": "Leave request rejected!"})

@app.route('/', methods=['GET'])
@token_required
def get_leave_requests():
    data_cuti = LeaveRequest.query.all()
    return render_template('home.html', data=data_cuti)
    # return jsonify(result)


@app.route("/logout", methods=["POST"])
@token_required
def logout():
    response = jsonify({"message": "Logged out successfully!"})
    response.delete_cookie("token")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
