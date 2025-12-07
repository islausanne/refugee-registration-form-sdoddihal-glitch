from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from werkzeug.utils import secure_filename

# -------------------- APP SETUP --------------------
app = Flask(__name__)  # Create the Flask application
app.secret_key = "supersecretkey"  # Required for flash messages (temporary messages to users)

# Set up folder to store uploaded images or documents
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it does not exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed file types for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

# -------------------- HELPER FUNCTION --------------------
def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    Returns True if the file is PNG, JPG, JPEG, or PDF.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- HOME PAGE --------------------
@app.route("/")
def index():
    """
    Home page route.
    Simply renders index.html.
    Can be used to add navigation or welcome text.
    """
    return render_template("index.html")

# -------------------- REGISTRATION FORM --------------------
@app.route("/register")
def register():
    """
    Displays the refugee registration form.
    User will fill in all personal information here.
    """
    return render_template("register.html")

# -------------------- FORM SUBMISSION --------------------
@app.route("/submit", methods=["POST"])
def submit_form():
    """
    Handles form submission when the user clicks 'Submit'.
    Steps:
    1. Collect input data from the form
    2. Validate all required fields and conditional fields
    3. Save uploaded files if provided
    4. Append the data to the JSON file
    5. Flash messages to show errors or success
    """

    # ----------- 1. COLLECT FORM INPUTS -----------
    # Use request.form.get() to avoid KeyErrors and .strip() to clean spaces
    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "")
    dob = request.form.get("dob", "")
    phone = request.form.get("phone", "").strip()
    id_type = request.form.get("id_type", "")
    id_value = request.form.get("id_value", "").strip()
    emergency_name = request.form.get("emergency_name", "").strip()
    emergency_phone = request.form.get("emergency_phone", "").strip()
    traveling_family = request.form.get("traveling_family", "").strip()
    medical_concerns = request.form.get("medical_concerns", "")
    medical_details = request.form.get("medical_details", "").strip()
    current_residence = request.form.get("current_residence", "").strip()
    image_file = request.files.get("image")  # User-uploaded image or document
    image_filename = None  # Will store filename if file is saved

    # ----------- 2. VALIDATION -----------
    error = False  # Flag to check if any validation fails

    # Validate required fields
    if not name:
        flash("Full Name is required", "error")
        error = True
    if not country:
        flash("Country of Origin is required", "error")
        error = True
    if not age:
        flash("Age is required", "error")
        error = True
    if age and (not age.isdigit() or int(age) <= 0):
        flash("Age must be a positive number", "error")
        error = True
    if not gender:
        flash("Gender is required", "error")
        error = True
    if not dob:
        flash("Date of Birth is required", "error")
        error = True
    if phone and not phone.isdigit():
        flash("Phone number must contain only digits", "error")
        error = True

    # Conditional validation: If user selects ID type, they must provide ID number
    if id_type and not id_value:
        flash(f"Please enter your {id_type} number", "error")
        error = True

    # Conditional validation: If user has medical concerns, they must specify details
    if medical_concerns == "Yes" and not medical_details:
        flash("Please specify your medical concerns", "error")
        error = True

    # File validation: Check if uploaded file exists and has allowed extension
    if image_file and image_file.filename != "":
        if not allowed_file(image_file.filename):
            flash("Invalid file type. Only PNG, JPG, JPEG, or PDF allowed.", "error")
            error = True
        else:
            # Save the file safely using secure_filename
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

    # Stop processing and redirect back to form if any validation fails
    if error:
        return redirect(url_for("register"))

    # ----------- 3. SAVE DATA TO JSON -----------
    # Load existing registrations if file exists, otherwise start with empty list
    if os.path.exists("registrations.json"):
        with open("registrations.json", "r") as file:
            data = json.load(file)
    else:
        data = []

    # Append the new registration as a dictionary
    data.append({
        "name": name,
        "country": country,
        "age": int(age),
        "gender": gender,
        "dob": dob,
        "phone": phone,
        "id_type": id_type,
        "id_value": id_value,
        "emergency_name": emergency_name,
        "emergency_phone": emergency_phone,
        "traveling_family": traveling_family,
        "medical_concerns": medical_concerns,
        "medical_details": medical_details,
        "current_residence": current_residence,
        "image_filename": image_filename
    })

    # Save updated registrations back to JSON
    with open("registrations.json", "w") as file:
        json.dump(data, file, indent=2)

    # ----------- 4. SUCCESS MESSAGE -----------
    flash("Registration submitted successfully!", "success")
    return redirect(url_for("register"))

# -------------------- VIEW REGISTRATIONS --------------------
@app.route("/view")
def view_registrations():
    """
    Reads all registrations from JSON and passes them to the template.
    If no registrations exist, sends an empty list.
    """
    if os.path.exists("registrations.json"):
        with open("registrations.json", "r") as file:
            data = json.load(file)
    else:
        data = []
    return render_template("view.html", registrations=data)

# -------------------- RUN THE APP --------------------
if __name__ == "__main__":
    # Run the app in debug mode to show errors during development
    app.run(debug=True)
