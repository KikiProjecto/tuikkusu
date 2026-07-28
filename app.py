from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "tuikkusu_secret_key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "tuikkusu"
app.config["MYSQL_PASSWORD"] = "tuikkusu123"
app.config["MYSQL_DB"] = "tweak_db"


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
        )
        return conn
    except mysql.connector.Error as err:
        flash(f"Gagal terhubung ke database: {err}", "error")
        return None


@app.route("/")
def index():
    conn = get_db_connection()
    records = []
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, kategori, item, ukuran, created_at FROM tb_pilihan")
            records = cursor.fetchall()
        except mysql.connector.Error as err:
            flash(f"Gagal memuat data: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            conn.close()
    return render_template("index.html", records=records)


@app.route("/add", methods=["POST"])
def add():
    kategori = request.form.get("kategori", "").strip()
    item = request.form.get("item", "").strip()
    try:
        ukuran = float(request.form.get("ukuran", 0))
    except ValueError:
        flash("Ukuran harus berupa angka!", "error")
        return redirect(url_for("index"))

    if not kategori or not item:
        flash("Kategori dan item tidak boleh kosong!", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("index"))

    cursor = None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO tb_pilihan (kategori, item, ukuran) VALUES (%s, %s, %s)"
        cursor.execute(sql, (kategori, item, ukuran))
        conn.commit()
        flash("Data berhasil ditambahkan!", "success")
    except mysql.connector.Error as err:
        flash(f"Gagal menambahkan data: {err}", "error")
    finally:
        if cursor:
            cursor.close()
        conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for("index"))

    cursor = None
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM tb_pilihan WHERE id=%s"
        cursor.execute(sql, (id,))
        conn.commit()
        flash(f"Record ID {id} berhasil dihapus!", "success")
    except mysql.connector.Error as err:
        flash(f"Gagal menghapus data: {err}", "error")
    finally:
        if cursor:
            cursor.close()
        conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
