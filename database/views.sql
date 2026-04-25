-- ============================================================
-- COMP3161 Course Management System — Report Views
-- ============================================================

-- 1. All courses that have 50 or more students enrolled
CREATE OR REPLACE VIEW v_courses_50plus_students AS
SELECT
    c.CourseID,
    c.CourseTitle,
    c.CourseCode,
    u.Name          AS LecturerName,
    COUNT(e.UserID) AS StudentCount
FROM Courses c
JOIN Enrolled e ON c.CourseID = e.CourseID
LEFT JOIN Users u ON c.LecID = u.UserID
GROUP BY c.CourseID, c.CourseTitle, c.CourseCode, u.Name
HAVING COUNT(e.UserID) >= 50
ORDER BY StudentCount DESC;


-- 2. All students enrolled in 5 or more courses
CREATE OR REPLACE VIEW v_students_5plus_courses AS
SELECT
    u.UserID,
    u.Name,
    u.Email,
    COUNT(e.CourseID) AS CourseCount
FROM Users u
JOIN Enrolled e ON u.UserID = e.UserID
WHERE u.AccountType = 'Student'
GROUP BY u.UserID, u.Name, u.Email
HAVING COUNT(e.CourseID) >= 5
ORDER BY CourseCount DESC;


-- 3. All lecturers that teach 3 or more courses
CREATE OR REPLACE VIEW v_lecturers_3plus_courses AS
SELECT
    u.UserID,
    u.Name,
    u.Email,
    COUNT(c.CourseID) AS CourseCount
FROM Users u
JOIN Courses c ON u.UserID = c.LecID
WHERE u.AccountType = 'Lecturer'
GROUP BY u.UserID, u.Name, u.Email
HAVING COUNT(c.CourseID) >= 3
ORDER BY CourseCount DESC;


-- 4. The 10 most enrolled courses
CREATE OR REPLACE VIEW v_top10_most_enrolled AS
SELECT
    c.CourseID,
    c.CourseTitle,
    c.CourseCode,
    u.Name          AS LecturerName,
    COUNT(e.UserID) AS EnrollmentCount
FROM Courses c
LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
LEFT JOIN Users u    ON c.LecID = u.UserID
GROUP BY c.CourseID, c.CourseTitle, c.CourseCode, u.Name
ORDER BY EnrollmentCount DESC
LIMIT 10;


-- 5. Top 10 students with the highest overall average
--    Overall average = mean percentage across all graded assignments
CREATE OR REPLACE VIEW v_top10_student_averages AS
SELECT
    u.UserID,
    u.Name,
    u.Email,
    ROUND(
        AVG((g.Grade / NULLIF(a.MaxGrade, 0)) * 100)::NUMERIC,
        2
    ) AS OverallAverage
FROM Users u
JOIN Submissions s ON u.UserID = s.StudentID
JOIN Grades      g ON s.SubmissionID = g.SubmissionID
JOIN Assignments a ON s.AssignmentID = a.AssignmentID
WHERE u.AccountType = 'Student'
GROUP BY u.UserID, u.Name, u.Email
ORDER BY OverallAverage DESC
LIMIT 10;
