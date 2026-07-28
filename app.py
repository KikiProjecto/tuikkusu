from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "tuikkusu_secret_key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "tuikkusu"
app.config["MYSQL_PASSWORD"] = "tuikkusu123"
app.config["MYSQL_DB"] = "tweak_db"

DEFAULT_CATEGORIES = {
    "-theme": {"navy": 9.4, "purple": 7.1, "green": 6.5, "red": 3.9, "yellow": 2.7},
    "-cursor": {"skyrim": 11.2, "hatsuneMiku": 13.5, "frierenBLZ": 7.8, "fluttershy": 9.3, "janeDoe": 15.9},
    "-shell": {"TST": 2.7, "obsidian": 2.5, "darkSolid": 1.9, "whiteSkin": 2.2, "retroSH": 1.2},
    "-icons": {"adwaita": 1.9, "MacTahoe": 1.3, "whitesur": 1.6, "overDose": 1.4, "Papirus": 1.2},
    "-fonts": {"inter": 0.5, "JetbrainsMono": 0.6, "poppins": 0.8, "SF Pro": 0.4, "TimesNewRoman": 0.2},
}


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


def load_categories_from_db():
    conn = get_db_connection()
    categories = {}
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT kategori, item, ukuran FROM tb_pilihan")
            rows = cursor.fetchall()
            for kategori, item, ukuran in rows:
                categories.setdefault(kategori, {})[item] = float(ukuran)
        except mysql.connector.Error as err:
            flash(f"Gagal memuat kategori: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            conn.close()
    if not categories:
        categories = DEFAULT_CATEGORIES
    return categories


@app.route("/", methods=["GET", "POST"])
def index():
    categories = load_categories_from_db()
    storage_limit = session.get("storage_limit", 0.0)
    selected = session.get("selected", {})
    selected_order = session.get("selected_order", [])
    total_used = session.get("total_used", 0.0)
    message = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "set_storage":
            try:
                storage_limit = float(request.form.get("storage", 0))
                session["storage_limit"] = storage_limit
                message = f"Storage diset ke {storage_limit} MB"
            except ValueError:
                flash("Storage harus berupa angka!", "error")
                return redirect(url_for("index"))

        elif action == "pilih":
            selected = {}
            selected_order = []
            for kategori, items in categories.items():
                item = request.form.get(f"tweak_{kategori}", "")
                if item and item in items:
                    ukuran = items[item]
                    key = f"{kategori} ({item})"
                    selected[key] = ukuran
                    selected_order.append(key)

            total_used = sum(selected.values())
            session["selected"] = selected
            session["selected_order"] = selected_order
            session["total_used"] = total_used
            message = f"Pilihan tersimpan: {len(selected_order)} item"

        elif action == "hapus_pilihan" and selected_order:
            hapus_key = request.form.get("hapus_key", "")
            if hapus_key in selected:
                selected.pop(hapus_key)
                if hapus_key in selected_order:
                    selected_order.remove(hapus_key)
                total_used = sum(selected.values())
                session["selected"] = selected
                session["selected_order"] = selected_order
                session["total_used"] = total_used
                message = f"Dihapus: {hapus_key}"

        elif action == "reset":
            conn = get_db_connection()
            if conn:
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute("TRUNCATE TABLE tb_pilihan")
                    conn.commit()
                except mysql.connector.Error as err:
                    flash(f"Gagal mereset database: {err}", "error")
                finally:
                    if cursor:
                        cursor.close()
                    conn.close()
            session.pop("selected", None)
            session.pop("selected_order", None)
            session.pop("total_used", None)
            session.pop("storage_limit", None)
            selected = {}
            selected_order = []
            total_used = 0.0
            storage_limit = 0.0
            message = "Semua data telah direset!"

        elif action == "simpan":
            conn = get_db_connection()
            if conn:
                cursor = None
                try:
                    cursor = conn.cursor()
                    sql = "INSERT INTO tb_pilihan (kategori, item, ukuran) VALUES (%s, %s, %s)"
                    for key, ukuran in selected.items():
                        kategori, item = key.split(" (", 1)
                        item = item.rstrip(")")
                        cursor.execute(sql, (kategori, item, ukuran))
                    conn.commit()
                    message = "Data berhasil disimpan ke database!"
                    session["selected"] = {}
                    session["selected_order"] = []
                    session["total_used"] = 0.0
                    selected = {}
                    selected_order = []
                    total_used = 0.0
                except mysql.connector.Error as err:
                    flash(f"Gagal menyimpan: {err}", "error")
                finally:
                    if cursor:
                        cursor.close()
                    conn.close()

        elif action == "muat":
            conn = get_db_connection()
            if conn:
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT kategori, item, ukuran FROM tb_pilihan")
                    rows = cursor.fetchall()
                    selected = {}
                    selected_order = []
                    for kategori, item, ukuran in rows:
                        key = f"{kategori} ({item})"
                        selected[key] = float(ukuran)
                        selected_order.append(key)
                    total_used = sum(selected.values())
                    session["selected"] = selected
                    session["selected_order"] = selected_order
                    session["total_used"] = total_used
                    message = f"Data dimuat: {len(rows)} records"
                except mysql.connector.Error as err:
                    flash(f"Gagal memuat data: {err}", "error")
                finally:
                    if cursor:
                        cursor.close()
                    conn.close()

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

    sisa = storage_limit - total_used
    return render_template(
        "index.html",
        categories=categories,
        storage_limit=storage_limit,
        selected=selected,
        selected_order=selected_order,
        total_used=total_used,
        sisa=sisa,
        records=records,
        message=message,
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    if conn:
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
