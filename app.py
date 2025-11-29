from flask import Flask, render_template, request
from abc import ABC, abstractmethod
from typing import List

app = Flask(__name__)

# -------------------------
# Models
# -------------------------
class Subject:
    def __init__(self, grade: str, credit: float):
        self.grade = grade.strip()
        self.credit = float(credit)

class Student:
    def __init__(self, name: str, subjects: List[Subject]):
        self.name = name.strip()
        self.subjects = subjects

class Semester:
    def __init__(self, gpa: float, credits: float):
        self.gpa = float(gpa)
        self.credits = float(credits)

# -------------------------
# Services
# -------------------------
class GradePointMap:
    MAP = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "F": 0.0
    }

    @classmethod
    def get_point(cls, grade):
        return cls.MAP.get(grade.upper(), 0.0)

class Calculator(ABC):
    @abstractmethod
    def calculate(self):
        pass

class GPACalculator(Calculator):
    def calculate(self, student: Student):
        total_points = 0
        total_credits = 0
        for s in student.subjects:
            total_points += GradePointMap.get_point(s.grade) * s.credit
            total_credits += s.credit
        return round(total_points / total_credits, 2) if total_credits else 0

class CGPACalculator(Calculator):
    def calculate(self, semesters: List[Semester]):
        total_points = 0
        total_credits = 0
        for s in semesters:
            total_points += s.gpa * s.credits
            total_credits += s.credits
        return round(total_points / total_credits, 2) if total_credits else 0

# -------------------------
# Validator
# -------------------------
class Validator:
    def positive_int(self, value, name):
        v = int(value)
        if v <= 0:
            raise ValueError(f"{name} must be positive")
        return v

    def positive_float(self, value, name):
        v = float(value)
        if v <= 0:
            raise ValueError(f"{name} must be positive")
        return v

    def gpa(self, value, name):
        v = float(value)
        if v < 0 or v > 4:
            raise ValueError(f"{name} must be between 0 and 4")
        return v

validator = Validator()
gpa_calc = GPACalculator()
cgpa_calc = CGPACalculator()

# -------------------------
# Routes
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    gpa = None
    cgpa = None
    error = ""
    calc_type = "gpa"
    student_name = ""

    if request.method == "POST":
        try:
            calc_type = request.form.get("calc_type")
            student_name = request.form.get("student", "").strip()

            # GPA Calculation
            if calc_type == "gpa":
                num = validator.positive_int(request.form["num_subjects"], "Subjects")
                subjects = []
                for i in range(1, num + 1):
                    grade = request.form[f"grade{i}"]
                    credit = validator.positive_float(request.form[f"credit{i}"], f"Credit {i}")
                    subjects.append(Subject(grade, credit))
                student = Student(student_name, subjects)
                gpa = gpa_calc.calculate(student)

            # CGPA Calculation
            else:
                num = validator.positive_int(request.form["num_semesters"], "Semesters")
                semesters = []
                for i in range(1, num + 1):
                    g = validator.gpa(request.form[f"sem_gpa{i}"], f"GPA {i}")
                    c = validator.positive_float(request.form[f"sem_credit{i}"], f"Credit {i}")
                    semesters.append(Semester(g, c))
                cgpa = cgpa_calc.calculate(semesters)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        gpa=gpa,
        cgpa=cgpa,
        error=error,
        calc_type=calc_type,
        student=student_name,
        submitted=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
