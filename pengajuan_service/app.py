from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from models import db, PengajuanCuti
from models import db, UserRole, TahunAjaran, Semester, SemesterStatus, Prodi, User
import jwt
from functools import wraps


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:password@db/sicuti"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"
bcrypt = Bcrypt(app)
db.init_app(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")  # Ambil token dari cookie
        if not token:
            return redirect("http://localhost:5003/")
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


@app.route("/logout", methods=["POST"])
@token_required
def logout():
    response = jsonify({"message": "Logged out successfully!"})
    response.delete_cookie("token")
    return response


@app.before_request
def create_tables():
    db.create_all()

    # seed_data()


@app.route("/", methods=["GET"])
@token_required
def welcome():
    return render_template("home.html")


@app.route("/apply_form", methods=["GET"])
@token_required
def apply_leave_form():
    return render_template("apply_form.html")


@app.route("/apply", methods=["POST"])
def apply():
    nama = request.form.get("nama")
    alasan = request.form.get("alasan")

    pengajuan = PengajuanCuti(nama=nama, alasan=alasan)
    db.session.add(pengajuan)
    db.session.commit()

    return jsonify({"message": "Leave application submitted successfully!"})


# bautian root untuk rollback database
@app.route("/rollback", methods=["GET"])
def rollback_data():
    db.drop_all()
    return jsonify({"message": "Database rollback successfully!"})


@app.route("/create_db", methods=["GET"])
def create_db():
    db.create_all()
    return jsonify({"message": "Database created successfully!"})


@app.route("/seeder", methods=["GET"])
def seed_data():
    with app.app_context():
        # Seed Tahun Ajaran
        if not TahunAjaran.query.first():
            tahun_ajaran1 = TahunAjaran(tahun="2023/2024", status=True)
            tahun_ajaran2 = TahunAjaran(tahun="2022/2023", status=False)
            db.session.add_all([tahun_ajaran1, tahun_ajaran2])
            db.session.commit()
            print("Seeded Tahun Ajaran!")

        # Seed Prodi
        if not Prodi.query.first():
            prodi1 = Prodi(nama="Teknik Informatika")
            prodi2 = Prodi(nama="Sistem Informasi")
            prodi3 = Prodi(nama="Teknik Elektro")
            prodi4 = Prodi(nama="Teknik Mesin")
            db.session.add_all([prodi1, prodi2, prodi3, prodi4])
            db.session.commit()
            print("Seeded Prodi!")

        # Seed Semester
        if not Semester.query.first():
            # Semester untuk tahun ajaran 2023/2024
            semester1 = Semester(
                semester=SemesterStatus.ganjil,
                tahun_ajaran_id=1,  # Referensi ke tahun ajaran 2023/2024
                status=True,
            )
            semester2 = Semester(
                semester=SemesterStatus.genap,
                tahun_ajaran_id=1,  # Referensi ke tahun ajaran 2023/2024
                status=False,
            )

            # Semester untuk tahun ajaran 2022/2023
            semester3 = Semester(
                semester=SemesterStatus.ganjil,
                tahun_ajaran_id=2,  # Referensi ke tahun ajaran 2022/2023
                status=False,
            )
            semester4 = Semester(
                semester=SemesterStatus.genap,
                tahun_ajaran_id=2,  # Referensi ke tahun ajaran 2022/2023
                status=False,
            )

            db.session.add_all([semester1, semester2, semester3, semester4])
            db.session.commit()
            print("Seeded Semester!")

        # Seed Users
        if not User.query.first():
            mahasiswa1 = User(
                nama="Ahmad Mahasiswa",
                username="mahasiswa1",
                password=bcrypt.generate_password_hash("mahasiswa123"),
                role=UserRole.mahasiswa,
                nim="123456789",
                prodi_id=1,  # Teknik Informatika
            )
            mahasiswa2 = User(
                nama="Budi Mahasiswa",
                username="mahasiswa2",
                password=bcrypt.generate_password_hash("mahasiswa123"),
                role=UserRole.mahasiswa,
                nim="987654321",
                prodi_id=2,  # Sistem Informasi
            )
            admin = User(
                nama="Admin BAK",
                username="admin",
                password=bcrypt.generate_password_hash("admin123"),
                role=UserRole.admin,
            )
            db.session.add_all([mahasiswa1, mahasiswa2, admin])
            db.session.commit()
            return jsonify({"message": "Seeded Users!"})


# @route("/register", methods=["POST"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
