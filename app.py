from flask import Flask, render_template, request, redirect, session
import pyodbc

app = Flask(__name__)

app.secret_key = "pmd_secret"


conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=DESKTOP-EIEOLQE\\SQLEXPRESS;"
    "DATABASE=pmd_internship;"
    "Trusted_Connection=yes;"
)


cursor = conn.cursor()


cursor.execute("SELECT @@SERVERNAME")
print("Server:", cursor.fetchone()[0])


cursor.execute("SELECT DB_NAME()")
print("Database:", cursor.fetchone()[0])


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")



# ADMIN LOGIN
@app.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]


        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT * FROM admin
            WHERE email=? AND password=?
            """,
            (email,password)
        )


        admin = cursor.fetchone()


        if admin:

            session["admin"] = email

            return redirect("/admin_dashboard")


        return "Invalid Admin Email or Password"


    return render_template("admin.html")




# ADMIN DASHBOARD
@app.route("/admin_dashboard")
def admin_dashboard():


    if "admin" not in session:
        return redirect("/admin")


    cursor = conn.cursor()



    # Total Students
    cursor.execute(
        "SELECT COUNT(*) FROM applications"
    )

    total = cursor.fetchone()[0]



    # Qualified
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM applications
        WHERE status='Qualified'
        """
    )

    qualified = cursor.fetchone()[0]



    # Not Qualified
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status='Not Qualified'
        """
    )

    notqualified = cursor.fetchone()[0]



    # Filter Students

    status = request.args.get("status")


    if status:


       cursor.execute(
    """
    SELECT
        application_id,
        fullname,
        email,
        university,
        semester,
        cgpa,
        department,
        resume,
        status
    FROM applications
    WHERE status=?
    """,
    (status,)
)

    else:


      cursor.execute("""
SELECT
    application_id,
    fullname,
    email,
    university,
    semester,
    cgpa,
    department,
    resume,
    status
FROM applications
""")


    columns = [column[0] for column in cursor.description]


    applicants = [
        dict(zip(columns,row))
        for row in cursor.fetchall()
    ]



    # Internships

    cursor.execute(
        """
        SELECT internship_id,
        title,
        department,
        duration,
        last_date
        FROM internships
        """
    )


    columns = [column[0] for column in cursor.description]


    internships = [
        dict(zip(columns,row))
        for row in cursor.fetchall()
    ]



    return render_template(
        "admin_dashboard.html",
        total=total,
        qualified=qualified,
        notqualified=notqualified,
        applicants=applicants,
        internships=internships
    )
    
# VIEW APPLICANT INFORMATION
@app.route("/view_applicant/<int:id>")
def view_applicant(id):

    if "admin" not in session:
        return redirect("/admin")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        WHERE application_id=?
    """, (id,))

    applicant = cursor.fetchone()

    if not applicant:
        return "Applicant Not Found"

    columns = [column[0] for column in cursor.description]

    applicant = dict(zip(columns, applicant))

    return render_template(
        "applicant_details.html",
        applicant=applicant
    )
    
    
    
    # QUALIFIED
@app.route("/qualified/<int:id>")
def qualified(id):

    if "admin" not in session:
        return redirect("/admin")


    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE applications
        SET status='Qualified'
        WHERE application_id=?
        """,
        (id,)
    )


    conn.commit()


    return redirect("/admin_dashboard")





# NOT QUALIFIED
@app.route("/notqualified/<int:id>")
def notqualified(id):

    if "admin" not in session:
        return redirect("/admin")


    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE applications
        SET status='Not Qualified'
        WHERE application_id=?
        """,
        (id,)
    )


    conn.commit()


    return redirect("/admin_dashboard")






# SIGNUP
@app.route("/signup", methods=["GET","POST"])
def signup():


    if request.method == "POST":


        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]


        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO students
            (fullname,email,password)
            VALUES(?,?,?)
            """,
            (fullname,email,password)
        )


        conn.commit()


        return redirect("/login")


    return render_template("signup.html")







# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():


    if request.method == "POST":


        email = request.form["email"]
        password = request.form["password"]


        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE email=? AND password=?
            """,
            (email,password)
        )


        user = cursor.fetchone()



        if user:

            session["user"] = email

            return redirect("/register")



        return "Invalid Email or Password"



    return render_template("login.html")








# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if "user" not in session:
        return redirect("/login")

    cursor = conn.cursor()

    # Check if already applied
    cursor.execute("""
        SELECT *
        FROM applications
        WHERE email=?
    """, (session["user"],))

    application = cursor.fetchone()

    if application:
        return render_template(
            "application_status.html",
            application=application
        )

    if request.method == "POST":

        # Personal Information
        fullname = request.form["fullname"]
        fathername = request.form["fathername"]
        email = request.form["email"]
        phone = request.form["phone"]
        cnic = request.form["cnic"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        address = request.form["address"]

        # Educational Information
        university = request.form["university"]
        degree = request.form["degree"]
        semester = request.form["semester"]
        graduation_year = request.form["graduation_year"]
        cgpa = request.form["cgpa"]
        department = request.form["department"]

        # Skills & Languages
        skills = request.form["skills"]
        languages = request.form["languages"]

        # Resume Upload
        resume = request.files["resume"]

        resume_name = ""

        if resume and resume.filename != "":
            resume_name = resume.filename
            resume.save("static/uploads/" + resume_name)

        # Save Data
        cursor.execute("""
            INSERT INTO applications
            (
                fullname,
                fathername,
                email,
                phone,
                cnic,
                dob,
                gender,
                address,
                university,
                degree,
                semester,
                graduation_year,
                cgpa,
                department,
                skills,
                languages,
                resume
            )
            VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            fullname,
            fathername,
            email,
            phone,
            cnic,
            dob,
            gender,
            address,
            university,
            degree,
            semester,
            graduation_year,
            cgpa,
            department,
            skills,
            languages,
            resume_name
        ))

        conn.commit()

        return render_template("success.html")

    return render_template("register.html")
# UPLOAD INTERNSHIP
@app.route("/upload_internship", methods=["GET","POST"])
def upload_internship():


    if "admin" not in session:

        return redirect("/admin")



    if request.method == "POST":


        title = request.form["title"]
        department = request.form["department"]
        duration = request.form["duration"]
        eligibility = request.form["eligibility"]
        skills = request.form["skills"]
        location = request.form["location"]
        last_date = request.form["last_date"]



        cursor = conn.cursor()



        cursor.execute(
            """
            INSERT INTO internships
            (
            title,
            department,
            duration,
            eligibility,
            skills,
            location,
            last_date
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                title,
                department,
                duration,
                eligibility,
                skills,
                location,
                last_date
            )
        )



        conn.commit()



        return redirect("/admin_dashboard")



    return render_template("upload_internship.html")







# DELETE INTERNSHIP
@app.route("/delete_internship/<int:id>")
def delete_internship(id):


    if "admin" not in session:

        return redirect("/admin")



    cursor = conn.cursor()



    cursor.execute(
        """
        DELETE FROM internships
        WHERE internship_id=?
        """,
        (id,)
    )



    conn.commit()



    return redirect("/admin_dashboard")







# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")








if __name__ == "__main__":

    app.run(debug=True)