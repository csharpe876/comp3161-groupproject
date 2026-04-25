-- ============================================================
-- COMP3161 Course Management System — Performance Indexes
-- ============================================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_account_type ON Users(AccountType);
CREATE INDEX IF NOT EXISTS idx_users_email        ON Users(Email);

-- Courses
CREATE INDEX IF NOT EXISTS idx_courses_lecid ON Courses(LecID);
CREATE INDEX IF NOT EXISTS idx_courses_code  ON Courses(CourseCode);

-- Enrolled (heavily queried for course roster lookups)
CREATE INDEX IF NOT EXISTS idx_enrolled_userid   ON Enrolled(UserID);
CREATE INDEX IF NOT EXISTS idx_enrolled_courseid ON Enrolled(CourseID);

-- CalendarEvents
CREATE INDEX IF NOT EXISTS idx_calendar_courseid  ON CalendarEvents(CourseID);
CREATE INDEX IF NOT EXISTS idx_calendar_eventdate ON CalendarEvents(EventDate);

-- Forums
CREATE INDEX IF NOT EXISTS idx_forums_courseid ON Forums(CourseID);

-- DiscussionThreads
CREATE INDEX IF NOT EXISTS idx_threads_forumid ON DiscussionThreads(ForumID);
CREATE INDEX IF NOT EXISTS idx_threads_userid  ON DiscussionThreads(UserID);

-- ThreadReplies
CREATE INDEX IF NOT EXISTS idx_replies_threadid ON ThreadReplies(ThreadID);
CREATE INDEX IF NOT EXISTS idx_replies_parentid ON ThreadReplies(ParentReplyID);
CREATE INDEX IF NOT EXISTS idx_replies_userid   ON ThreadReplies(UserID);

-- ContentSections
CREATE INDEX IF NOT EXISTS idx_sections_courseid ON ContentSections(CourseID);

-- CourseContent
CREATE INDEX IF NOT EXISTS idx_content_sectionid ON CourseContent(SectionID);
CREATE INDEX IF NOT EXISTS idx_content_type      ON CourseContent(ContentType);

-- Assignments
CREATE INDEX IF NOT EXISTS idx_assignments_courseid ON Assignments(CourseID);
CREATE INDEX IF NOT EXISTS idx_assignments_duedate  ON Assignments(DueDate);

-- Submissions
CREATE INDEX IF NOT EXISTS idx_submissions_assignmentid ON Submissions(AssignmentID);
CREATE INDEX IF NOT EXISTS idx_submissions_studentid    ON Submissions(StudentID);

-- Grades
CREATE INDEX IF NOT EXISTS idx_grades_submissionid ON Grades(SubmissionID);
CREATE INDEX IF NOT EXISTS idx_grades_gradedby     ON Grades(GradedBy);
