from faker import Faker
from collections import defaultdict
import random
import hashlib

fake = Faker()
f = open("project_insert_data.sql", "w")

NUM_STUDENTS = 100_000
NUM_COURSES = 200
MIN_COURSES_PER_STUDENT = 3
MAX_COURSES_PER_STUDENT = 6
MIN_STUDENTS_PER_COURSE = 10
MAX_COURSES_PER_LECTURER = 5
NUM_LECTURERS = NUM_COURSES // MAX_COURSES_PER_LECTURER
dept = []


def generate_users(NUM_STUDENTS, NUM_LECTURERS):
    users = []
    # Lecturers
    for i in range(1, NUM_LECTURERS+1):
        lec_id = f"L{i}"
        fname = fake.first_name()
        lname = fake.last_name()
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}@uwi.edu"
        password = hashlib.sha256(f"{fname}{lname}{i}".encode()).hexdigest()
        account_type = 'Lecturer'
        users.append({'id': lec_id, 'password': password, 'name': name, 'email': email, 'type': account_type})
        f.write(f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) VALUES('{lec_id}', '{password}', '{name}', '{email}', '{account_type}');\n")
    # Students
    for i in range(1, NUM_STUDENTS+1):
        student_id = f"S{i}"
        fname = fake.first_name()
        lname = fake.last_name()
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}@uwi.edu"
        password = hashlib.sha256(f"{fname}{lname}{i}".encode()).hexdigest()
        account_type = 'Student'
        users.append({'id': student_id, 'password': password, 'name': name, 'email': email, 'type': account_type})
        f.write(f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) VALUES('{student_id}', '{password}', '{name}', '{email}', '{account_type}');\n")
    return users

def generate_departments(n=20):
    departments = set()
    # Use a mix of common academic departments and Faker-generated plausible names
    common_depts = [
        'Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
        'Economics', 'History', 'Philosophy', 'Engineering', 'Psychology',
        'Sociology', 'Political Science', 'Business', 'Education', 'Art',
        'Music', 'Geography', 'Statistics', 'Medicine', 'Law'
    ]
    for dept in common_depts:
        departments.add(dept + ' Department')
        if len(departments) >= n:
            break
    while len(departments) < n:
        # Use job or company for plausible department names
        dept = fake.unique.job().split()[-1].capitalize() + ' Department'
        departments.add(dept)
    return list(departments)

def generate_courses(NUM_COURSES, departments, lec_id):
    courses = []
    lecturer_course_count = defaultdict(int)
    # Assign one course to each lecturer
    for i, lec in enumerate(lec_id):
        if len(courses) >= NUM_COURSES:
            break
        course_id = f"C{len(courses)+1}"
        dept = random.choice(departments)
        cname = fake.catch_phrase()
        ccode = dept.replace(" ", "")[:4].upper() + str(random.randint(1000, 3999))
        f.write(f"INSERT INTO Courses(CourseID, CourseTitle, CourseCode, LecID) VALUES('{course_id}', '{cname}', '{ccode}', '{lec}');\n")
        courses.append({'id': course_id, 'dept': dept, 'name': cname, 'code': ccode, 'lecturer': lec})
        lecturer_course_count[lec] += 1
    # Assign remaining courses, ensuring no lecturer has >5
    while len(courses) < NUM_COURSES:
        possible_lecs = [lec for lec in lec_id if lecturer_course_count[lec] < MAX_COURSES_PER_LECTURER]
        lec = random.choice(possible_lecs)
        course_id = f"C{len(courses)+1}"
        dept = random.choice(departments)
        cname = fake.catch_phrase()
        ccode = dept.replace(" ", "")[:4].upper() + str(random.randint(1000, 3999))
        f.write(f"INSERT INTO Courses(CourseID, CourseTitle, CourseCode, LecID) VALUES('{course_id}', '{cname}', '{ccode}', '{lec}');\n")
        courses.append({'id': course_id, 'dept': dept, 'name': cname, 'code': ccode, 'lecturer': lec})
        lecturer_course_count[lec] += 1
    return courses

def enroll_students(NUM_STUDENTS, courses):
    course_members = defaultdict(set)
    student_ids = [f"S{i}" for i in range(1, NUM_STUDENTS+1)]
    # Ensure each course has at least 10 unique students
    for course in courses:
        members = set(random.sample(student_ids, MIN_STUDENTS_PER_COURSE))
        course_members[course['id']].update(members)
        for sid in members:
            f.write(f"INSERT INTO Enrolled(UserID, CourseID) VALUES('{sid}', '{course['id']}');\n")
    # Assign each student to 3-6 courses
    for sid in student_ids:
        already = set([c for c in course_members if sid in course_members[c]])
        n_courses = random.randint(MIN_COURSES_PER_STUDENT, MAX_COURSES_PER_STUDENT)
        needed = n_courses - len(already)
        if needed > 0:
            available = [c['id'] for c in courses if sid not in course_members[c['id']]]
            chosen = random.sample(available, min(needed, len(available)))
            for cid in chosen:
                course_members[cid].add(sid)
                f.write(f"INSERT INTO Enrolled(UserID, CourseID) VALUES('{sid}', '{cid}');\n")

def main():
    departments = generate_departments()
    users = generate_users(NUM_STUDENTS, NUM_LECTURERS)
    lecturer_ids = [u['id'] for u in users if u['type'] == 'Lecturer']
    courses = generate_courses(NUM_COURSES, departments, lecturer_ids)
    enroll_students(NUM_STUDENTS, courses)
    f.close()
    print("Data generation complete. SQL statements written to project_insert_data.sql")

if __name__ == "__main__":
    main()