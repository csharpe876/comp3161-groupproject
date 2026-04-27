from faker import Faker
from collections import defaultdict
import random
import hashlib
import bcrypt

fake = Faker()
f = open("project_insert_data.sql", "w")

NUM_STUDENTS            = 100_000
NUM_COURSES             = 200
NUM_ADMINS              = 3
MIN_COURSES_PER_STUDENT = 3
MAX_COURSES_PER_STUDENT = 6
MIN_STUDENTS_PER_COURSE = 10
MAX_COURSES_PER_LECTURER = 5
NUM_LECTURERS           = NUM_COURSES // MAX_COURSES_PER_LECTURER

# New-table generation parameters
FORUMS_PER_COURSE      = (2, 4)
THREADS_PER_FORUM      = (2, 5)
REPLIES_PER_THREAD     = (1, 6)
SECTIONS_PER_COURSE    = (2, 4)
CONTENT_PER_SECTION    = (2, 5)
ASSIGNMENTS_PER_COURSE = (2, 4)
EVENTS_PER_COURSE      = (2, 4)
SUBMISSION_RATE        = 0.30   # fraction of enrolled students who submit per assignment
GRADE_RATE             = 0.80   # fraction of submissions that receive a grade


def esc(s):
    """Escape single quotes for SQL string literals."""
    return str(s).replace("'", "''")


def generate_users(NUM_STUDENTS, NUM_LECTURERS, NUM_ADMINS):
    users = []
    # Admins
    for i in range(1, NUM_ADMINS + 1):
        admin_id = f"A{i}"
        fname = fake.first_name()
        lname = fake.last_name()
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}@uwi.edu"
        password = hashlib.sha256(f"{fname}{lname}".encode()).hexdigest()
        users.append({'id': admin_id, 'name': name, 'email': email, 'type': 'Admin'})
        f.write(f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) VALUES('{admin_id}', '{password}', '{esc(name)}', '{esc(email)}', 'Admin');\n")
    # Lecturers
    for i in range(1, NUM_LECTURERS + 1):
        lec_id = f"L{i}"
        fname = fake.first_name()
        lname = fake.last_name()
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}@uwi.edu"
        password = hashlib.sha256(f"{fname}{lname}".encode()).hexdigest()
        users.append({'id': lec_id, 'name': name, 'email': email, 'type': 'Lecturer'})
        f.write(f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) VALUES('{lec_id}', '{password}', '{esc(name)}', '{esc(email)}', 'Lecturer');\n")
    # Students
    for i in range(1, NUM_STUDENTS + 1):
        student_id = f"S{i}"
        fname = fake.first_name()
        lname = fake.last_name()
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}@uwi.edu"
        password = hashlib.sha256(f"{fname}{lname}".encode()).hexdigest()
        users.append({'id': student_id, 'name': name, 'email': email, 'type': 'Student'})
        f.write(f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) VALUES('{student_id}', '{password}', '{esc(name)}', '{esc(email)}', 'Student');\n")
    return users


def generate_departments(n=20):
    common_depts = [
        'Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
        'Economics', 'History', 'Philosophy', 'Engineering', 'Psychology',
        'Sociology', 'Political Science', 'Business', 'Education', 'Art',
        'Music', 'Geography', 'Statistics', 'Medicine', 'Law'
    ]
    return [d + ' Department' for d in common_depts[:n]]


def generate_courses(NUM_COURSES, departments, lec_ids):
    courses = []
    lecturer_course_count = defaultdict(int)
    # Assign one course to each lecturer first
    for lec in lec_ids:
        if len(courses) >= NUM_COURSES:
            break
        course_id = f"C{len(courses) + 1}"
        dept = random.choice(departments)
        cname = fake.catch_phrase()
        ccode = dept.replace(" ", "")[:4].upper() + str(random.randint(1000, 3999))
        desc = fake.sentence(nb_words=10)
        f.write(f"INSERT INTO Courses(CourseID, CourseTitle, CourseCode, Description, LecID) VALUES('{course_id}', '{esc(cname)}', '{ccode}', '{esc(desc)}', '{lec}');\n")
        courses.append({'id': course_id, 'dept': dept, 'name': cname, 'code': ccode, 'lecturer': lec})
        lecturer_course_count[lec] += 1
    # Fill remaining courses, respecting per-lecturer cap
    while len(courses) < NUM_COURSES:
        possible_lecs = [l for l in lec_ids if lecturer_course_count[l] < MAX_COURSES_PER_LECTURER]
        lec = random.choice(possible_lecs)
        course_id = f"C{len(courses) + 1}"
        dept = random.choice(departments)
        cname = fake.catch_phrase()
        ccode = dept.replace(" ", "")[:4].upper() + str(random.randint(1000, 3999))
        desc = fake.sentence(nb_words=10)
        f.write(f"INSERT INTO Courses(CourseID, CourseTitle, CourseCode, Description, LecID) VALUES('{course_id}', '{esc(cname)}', '{ccode}', '{esc(desc)}', '{lec}');\n")
        courses.append({'id': course_id, 'dept': dept, 'name': cname, 'code': ccode, 'lecturer': lec})
        lecturer_course_count[lec] += 1
    return courses


def enroll_students(NUM_STUDENTS, courses):
    """Returns course_members: dict[course_id -> set of student_ids]."""
    course_members = defaultdict(set)
    student_ids = [f"S{i}" for i in range(1, NUM_STUDENTS + 1)]
    # Ensure each course has at least MIN_STUDENTS_PER_COURSE unique students
    for course in courses:
        members = set(random.sample(student_ids, MIN_STUDENTS_PER_COURSE))
        course_members[course['id']].update(members)
        for sid in members:
            f.write(f"INSERT INTO Enrolled(UserID, CourseID) VALUES('{sid}', '{course['id']}');\n")
    # Assign each student to 3–6 courses
    for sid in student_ids:
        already = {cid for cid, members in course_members.items() if sid in members}
        n_courses = random.randint(MIN_COURSES_PER_STUDENT, MAX_COURSES_PER_STUDENT)
        needed = n_courses - len(already)
        if needed > 0:
            available = [c['id'] for c in courses if sid not in course_members[c['id']]]
            chosen = random.sample(available, min(needed, len(available)))
            for cid in chosen:
                course_members[cid].add(sid)
                f.write(f"INSERT INTO Enrolled(UserID, CourseID) VALUES('{sid}', '{cid}');\n")
    return course_members


def generate_calendar_events(courses):
    for course in courses:
        n = random.randint(*EVENTS_PER_COURSE)
        for _ in range(n):
            title = esc(fake.catch_phrase())
            desc = esc(fake.sentence(nb_words=8))
            event_date = fake.date_between(start_date='-1y', end_date='+1y').isoformat()
            event_time = fake.time()
            created_by = course['lecturer']
            f.write(
                f"INSERT INTO CalendarEvents(CourseID, Title, Description, EventDate, EventTime, CreatedBy) "
                f"VALUES('{course['id']}', '{title}', '{desc}', '{event_date}', '{event_time}', '{created_by}');\n"
            )


def generate_forums(courses):
    """Returns list of forum dicts with sequential SERIAL IDs."""
    forums = []
    forum_id = 1
    for course in courses:
        n = random.randint(*FORUMS_PER_COURSE)
        for _ in range(n):
            title = esc(fake.catch_phrase())
            desc = esc(fake.sentence(nb_words=10))
            created_by = course['lecturer']
            f.write(
                f"INSERT INTO Forums(CourseID, Title, Description, CreatedBy) "
                f"VALUES('{course['id']}', '{title}', '{desc}', '{created_by}');\n"
            )
            forums.append({'id': forum_id, 'course_id': course['id']})
            forum_id += 1
    return forums


def generate_threads(forums, all_user_ids):
    """Returns list of thread dicts with sequential SERIAL IDs."""
    threads = []
    thread_id = 1
    for forum in forums:
        n = random.randint(*THREADS_PER_FORUM)
        for _ in range(n):
            uid = random.choice(all_user_ids)
            title = esc(fake.sentence(nb_words=6).rstrip('.'))
            content = esc(fake.paragraph(nb_sentences=3))
            f.write(
                f"INSERT INTO DiscussionThreads(ForumID, UserID, Title, Content) "
                f"VALUES({forum['id']}, '{uid}', '{title}', '{content}');\n"
            )
            threads.append({'id': thread_id, 'forum_id': forum['id']})
            thread_id += 1
    return threads


def generate_replies(threads, all_user_ids):
    reply_id = 1
    for thread in threads:
        n = random.randint(*REPLIES_PER_THREAD)
        thread_reply_ids = []
        for _ in range(n):
            uid = random.choice(all_user_ids)
            content = esc(fake.paragraph(nb_sentences=2))
            # ~40% chance a reply is nested under a previous reply in the same thread
            if thread_reply_ids and random.random() < 0.4:
                parent_id = random.choice(thread_reply_ids)
                f.write(
                    f"INSERT INTO ThreadReplies(ThreadID, ParentReplyID, UserID, Content) "
                    f"VALUES({thread['id']}, {parent_id}, '{uid}', '{content}');\n"
                )
            else:
                f.write(
                    f"INSERT INTO ThreadReplies(ThreadID, ParentReplyID, UserID, Content) "
                    f"VALUES({thread['id']}, NULL, '{uid}', '{content}');\n"
                )
            thread_reply_ids.append(reply_id)
            reply_id += 1


def generate_content_sections(courses):
    """Returns list of section dicts with sequential SERIAL IDs."""
    section_name_pool = [
        'Introduction', 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5',
        'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11',
        'Week 12', 'Midterm Review', 'Final Review', 'Supplementary Material',
        'Project Resources', 'Lab Exercises', 'Readings', 'Assignments',
    ]
    sections = []
    section_id = 1
    for course in courses:
        n = random.randint(*SECTIONS_PER_COURSE)
        chosen_names = random.sample(section_name_pool, n)
        for idx, sname in enumerate(chosen_names):
            f.write(
                f"INSERT INTO ContentSections(CourseID, SectionName, OrderIndex) "
                f"VALUES('{course['id']}', '{sname}', {idx});\n"
            )
            sections.append({'id': section_id, 'course_id': course['id']})
            section_id += 1
    return sections


def generate_course_content(sections):
    content_types = ['link', 'file', 'slide']
    for section in sections:
        n = random.randint(*CONTENT_PER_SECTION)
        for _ in range(n):
            title = esc(fake.catch_phrase())
            ctype = random.choice(content_types)
            url = fake.url()
            desc = esc(fake.sentence(nb_words=8))
            f.write(
                f"INSERT INTO CourseContent(SectionID, Title, ContentType, ContentURL, Description) "
                f"VALUES({section['id']}, '{title}', '{ctype}', '{url}', '{desc}');\n"
            )


def generate_assignments(courses):
    """Returns list of assignment dicts with sequential SERIAL IDs."""
    assignments = []
    assignment_id = 1
    for course in courses:
        n = random.randint(*ASSIGNMENTS_PER_COURSE)
        for i in range(1, n + 1):
            title = esc(f"Assignment {i}: {fake.catch_phrase()}")
            desc = esc(fake.sentence(nb_words=12))
            due_date = fake.date_time_between(start_date='-6m', end_date='+6m').strftime('%Y-%m-%d %H:%M:%S')
            max_grade = random.choice([50, 100])
            f.write(
                f"INSERT INTO Assignments(CourseID, Title, Description, DueDate, MaxGrade) "
                f"VALUES('{course['id']}', '{title}', '{desc}', '{due_date}', {max_grade});\n"
            )
            assignments.append({'id': assignment_id, 'course_id': course['id'], 'max_grade': max_grade})
            assignment_id += 1
    return assignments


def generate_submissions_and_grades(assignments, course_members, course_lecturer):
    """
    For each assignment, SUBMISSION_RATE of enrolled students submit.
    GRADE_RATE of those submissions are then graded by the course lecturer.
    """
    submission_id = 1
    for assignment in assignments:
        cid = assignment['course_id']
        students = list(course_members.get(cid, []))
        if not students:
            continue
        n_submit = max(1, int(len(students) * SUBMISSION_RATE))
        submitting = random.sample(students, min(n_submit, len(students)))
        for sid in submitting:
            content = esc(fake.paragraph(nb_sentences=4))
            submitted_at = fake.date_time_between(start_date='-6m', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            f.write(
                f"INSERT INTO Submissions(AssignmentID, StudentID, Content, SubmittedAt) "
                f"VALUES({assignment['id']}, '{sid}', '{content}', '{submitted_at}');\n"
            )
            if random.random() < GRADE_RATE:
                grade = round(random.uniform(0, assignment['max_grade']), 2)
                graded_by = course_lecturer.get(cid, '')
                graded_at = fake.date_time_between(start_date='-3m', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
                f.write(
                    f"INSERT INTO Grades(SubmissionID, Grade, GradedBy, GradedAt) "
                    f"VALUES({submission_id}, {grade}, '{graded_by}', '{graded_at}');\n"
                )
            submission_id += 1


def generate_test_users():
    """Insert 3 fixed test users (student/lecturer/admin) with bcrypt passwords."""
    test_users = [
        ('test_student',  'student123',  'Test Student',  'test.student@uwi.edu',  'Student'),
        ('test_lecturer', 'lecturer123', 'Test Lecturer', 'test.lecturer@uwi.edu', 'Lecturer'),
        ('test_admin',    'admin123',    'Test Admin',    'test.admin@uwi.edu',    'Admin'),
    ]
    for uid, pw, name, email, atype in test_users:
        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        f.write(
            f"INSERT INTO Users(UserID, Password, Name, Email, AccountType) "
            f"VALUES('{uid}', '{hashed}', '{name}', '{email}', '{atype}') "
            f"ON CONFLICT (UserID) DO UPDATE SET Password=EXCLUDED.Password;\n"
        )


def main():
    departments = generate_departments()
    users = generate_users(NUM_STUDENTS, NUM_LECTURERS, NUM_ADMINS)
    lecturer_ids = [u['id'] for u in users if u['type'] == 'Lecturer']
    all_user_ids = [u['id'] for u in users]
    courses = generate_courses(NUM_COURSES, departments, lecturer_ids)

    course_lecturer = {c['id']: c['lecturer'] for c in courses}
    course_members = enroll_students(NUM_STUDENTS, courses)

    generate_calendar_events(courses)

    forums = generate_forums(courses)
    threads = generate_threads(forums, all_user_ids)
    generate_replies(threads, all_user_ids)

    sections = generate_content_sections(courses)
    generate_course_content(sections)

    assignments = generate_assignments(courses)
    generate_submissions_and_grades(assignments, course_members, course_lecturer)

    generate_test_users()

    f.close()
    print("Data generation complete. SQL statements written to project_insert_data.sql")
    print("Test users included: test_student/student123, test_lecturer/lecturer123, test_admin/admin123")


if __name__ == "__main__":
    main()