from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, make_response
from werkzeug.utils import secure_filename
from datetime import datetime
from io import StringIO
import csv
import os

app = Flask(__name__)
app.secret_key = "auto-print-secret"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
ADMIN_PASSWORD = "2026080315"
STATUSES = ["En attente", "En impression", "Prête à envoyer", "Envoyée"]

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

orders = []
next_order_id = 1

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required():
    return session.get("admin") is True


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/produits")
def produits():
    return render_template("products.html")


@app.route("/commander", methods=["GET", "POST"])
def commander():
    global next_order_id

    if request.method == "POST":
        nom = request.form.get("nom")
        email = request.form.get("email")
        product_type = request.form.get("product_type")
        quantite = request.form.get("quantite")
        adresse_type = request.form.get("adresse_type")
        adresse_detail = request.form.get("adresse_detail")
        message = request.form.get("message")
        photo = request.files.get("photo")

        if not nom or not email or not product_type or not quantite or not adresse_type:
            flash("Merci de remplir tous les champs obligatoires.", "error")
            return redirect(url_for("commander"))

        if adresse_type == "Autre" and not adresse_detail:
            flash("Merci de préciser l'adresse si vous choisissez 'Autre'.", "error")
            return redirect(url_for("commander"))

        if adresse_type == "Autre":
            adresse = f"Autre : {adresse_detail.strip()}"
        else:
            adresse = adresse_type

        if not photo or photo.filename == "":
            flash("Merci d'ajouter une photo JPG ou PNG.", "error")
            return redirect(url_for("commander"))

        if not allowed_file(photo.filename):
            flash("Le format du fichier doit être JPG ou PNG.", "error")
            return redirect(url_for("commander"))

        filename = f"{next_order_id}_{secure_filename(photo.filename)}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(save_path)

        now = datetime.now()
        order = {
            "id": next_order_id,
            "nom": nom,
            "email": email,
            "product_type": "Autocollant" if product_type == "autocollant" else "Carte postale",
            "quantite": quantite,
            "adresse": adresse,
            "message": message,
            "photo_filename": filename,
            "status": "En attente",
            "date": now.strftime("%d/%m/%Y"),
            "date_iso": now.strftime("%Y-%m-%d"),
        }
        orders.append(order)
        next_order_id += 1
        flash("Votre commande a bien été enregistrée. Nous reviendrons vers vous rapidement !", "success")
        return redirect(url_for("merci"))

    return render_template("order.html")


@app.route("/merci")
def merci():
    return render_template("merci.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/admin")
def admin():
    if admin_required():
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("admin_login"))


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Mot de passe incorrect.", "error")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    flash("Déconnexion réussie.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin-dashboard")
def admin_dashboard():
    if not admin_required():
        flash("Merci de vous connecter pour accéder au tableau de bord.", "error")
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "").strip().lower()
    status_filter = request.args.get("status", "")
    date_filter = request.args.get("date", "")

    filtered_orders = orders
    if search:
        filtered_orders = [o for o in filtered_orders if search in o["nom"].lower() or search in o["email"].lower()]
    if status_filter:
        filtered_orders = [o for o in filtered_orders if o["status"] == status_filter]
    if date_filter:
        filtered_orders = [o for o in filtered_orders if o["date_iso"] == date_filter]

    return render_template(
        "admin_dashboard.html",
        orders=filtered_orders,
        statuses=STATUSES,
        filters={
            "search": request.args.get("search", ""),
            "status": status_filter,
            "date_iso": date_filter,
        },
    )


@app.route("/admin-update-status", methods=["POST"])
def admin_update_status():
    if not admin_required():
        flash("Accès refusé.", "error")
        return redirect(url_for("admin_login"))

    order_id = request.form.get("order_id")
    new_status = request.form.get("new_status")
    if order_id and new_status in STATUSES:
        for order in orders:
            if str(order["id"]) == str(order_id):
                order["status"] = new_status
                flash(f"Statut de la commande {order_id} mis à jour.", "success")
                break
    return redirect(url_for("admin_dashboard"))


@app.route("/admin-export-csv")
def admin_export_csv():
    if not admin_required():
        flash("Accès refusé.", "error")
        return redirect(url_for("admin_login"))

    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["ID", "Nom Client", "Email", "Produit", "Quantité", "Photo", "Adresse", "Message", "Statut", "Date"])
    for order in orders:
        writer.writerow([
            order["id"],
            order["nom"],
            order["email"],
            order["product_type"],
            order["quantite"],
            order["photo_filename"],
            order["adresse"],
            order["message"],
            order["status"],
            order["date"],
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=commandes_autoprint.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(debug=True, host="0.0.0.0", port=port)
