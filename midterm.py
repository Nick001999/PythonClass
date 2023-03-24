import csv

class Student:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.courses = {}

class Course:
    def __init__(self, id, name, credit):
        self.id = id
        self.name = name
        self.credit = credit
        self.students = {}

class Enrollment:
    def __init__(self, student_id, course_id, semester, grade):
        self.student_id = student_id
        self.course_id = course_id
        self.semester = semester
        self.grade = grade

class FinalCode:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.enrollments = []

    def load_data(self):
        with open('students.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                student = Student(row[0], row[1], row[2])
                self.students[row[0]] = student

        with open('courses.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                course = Course(row[0], row[1], row[2])
                self.courses[row[0]] = course

        with open('enrollments.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                enrollment = Enrollment(row[0], row[1], row[2], row[3])
                self.enrollments.append(enrollment)

    def display_menu(self):
        print("1. Add Student")
        print("2. Enroll Student to Course")
        print("3. Grade Student")
        print("4. Display Student")
        print("5. Display Course")
        print("0. Exit")

    def add_student(self):
        id = input("Enter Student ID: ")
        name = input("Enter Student Name: ")
        email = input("Enter Student Email: ")
        student = Student(id, name, email)
        self.students[id] = student
        print("Student Added Successfully!")

    def enroll_student(self):
        student_id = input("Enter Student ID: ")
        course_id = input("Enter Course ID: ")
        semester = input("Enter Semester: ")
        enrollment = Enrollment(student_id, course_id, semester, "")
        self.enrollments.append(enrollment)
        self.students[student_id].courses[course_id] = semester
        self.courses[course_id].students[student_id] = semester
        print("Student Enrolled Successfully!")

    def grade_student(self):
        student_id = input("Enter Student ID: ")
        course_id = input("Enter Course ID: ")
        grade = input("Enter Grade: ")
        for enrollment in self.enrollments:
            if enrollment.student_id == student_id and enrollment.course_id == course_id:
                enrollment.grade = grade
                self.students[student_id].courses[course_id] = grade
                self.courses[course_id].students[student_id] = grade
                print("Grade Added Successfully!")
                return
        print("This Student is not enrolled in this Course!")

    def display_student(self):
        student_id = input("Enter Student ID: ")
        if student_id in self.students:
            student = self.students[student_id]
            print("Student ID:", student.id)
            print("Student Name:", student.name)
            print("Student Email:", student.email)
            print("Courses Enrolled:")
            for course_id, semester in student.courses.items():
                print(course_id, "-", self.courses[course_id].name, "-", semester, "-", self.courses[course_id].credit, "credits")
        else:
            print("Student not found!")

    def display_course(self):
        course_id = input("Enter Course ID: ")
        if course_id in self.courses:
            course = self.courses[course_id]
            print("Course ID:", course.id)
            print("Course Name:", course.name)
            print("Course Credit:", course.credit)
            print("Students Enrolled:")
            for student_id, semester in course.students.items():
                print(student_id, "-", self.students[student_id].name, "-", semester)
        else:
            print("Course not found!")

    def run(self):
        self.load_data()
        choice = -1
        while choice != 0:
            self.display_menu()
            choice = int(input("Enter Your Choice: "))
            if choice == 1:
                self.add_student()
            elif choice == 2:
                self.enroll_student()
            elif choice == 3:
                self.grade_student()
            elif choice == 4:
                self.display_student()
            elif choice == 5:
                self.display_course()
            elif choice == 0:
                print("Bye...")
            else:
                print("Invalid Choice! Try again!")

finalcode = FinalCode()
finalcode.run()
