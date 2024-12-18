from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, UserRole, TahunAjaran, Semester, SemesterStatus, Prodi, User


def rollback_data(app):
    """
    Menghapus semua data dari tabel-tabel yang akan di-seed
    Urutan penghapusan penting untuk menghindari constraint violation
    """
    with app.app_context():
        try:
            # Hapus data dari tabel-tabel sesuai urutan
            User.query.delete()
            Semester.query.delete()
            TahunAjaran.query.delete()
            Prodi.query.delete()

            # Commit perubahan
            db.session.commit()
            print("Rollback data selesai!")
        except Exception as e:
            # Rollback jika terjadi kesalahan
            db.session.rollback()
            print(f"Error saat rollback: {e}")


def seed_data(app):
    with app.app_context():
        # Buat tabel jika belum ada
        db.create_all()

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
                password=generate_password_hash("mahasiswa123", method="pbkdf2:sha256"),
                role=UserRole.mahasiswa,
                nim="123456789",
                prodi_id=1,  # Teknik Informatika
            )
            mahasiswa2 = User(
                nama="Budi Mahasiswa",
                username="mahasiswa2",
                password=generate_password_hash("mahasiswa123", method="pbkdf2:sha256"),
                role=UserRole.mahasiswa,
                nim="987654321",
                prodi_id=2,  # Sistem Informasi
            )
            admin = User(
                nama="Admin BAK",
                username="admin",
                password=generate_password_hash("admin123", method="pbkdf2:sha256"),
                role=UserRole.admin,
            )
            db.session.add_all([mahasiswa1, mahasiswa2, admin])
            db.session.commit()
            print("Seeded Users!")


# Tambahkan kode untuk menjalankan seeding
if __name__ == "__main__":

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:password@db/sicuti"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # Inisialisasi db dengan app
    db.init_app(app)

    # rollback_data(app)

    # Panggil fungsi seeding
    seed_data(app)
    # print("Seeding selesai!")
    # with app.app_context():
    #     print("Connected to database:", db.engine.url.database)
