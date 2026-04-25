-- ============================================================
-- COMP3161 Course Management System — Database Schema
-- PostgreSQL 16
-- ============================================================

-- Users: admins, lecturers, students
-- NOTE: Seeded users (from insertdata.py) use SHA-256 passwords.
--       Users registered through the API use bcrypt hashes.
CREATE TABLE IF NOT EXISTS Users (
    UserID      VARCHAR(20)  PRIMARY KEY,
    Password    VARCHAR(255) NOT NULL,
    Name        VARCHAR(100) NOT NULL,
    Email       VARCHAR(150) NOT NULL UNIQUE,
    AccountType VARCHAR(10)  NOT NULL CHECK (AccountType IN ('Admin', 'Lecturer', 'Student')),
    CreatedAt   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Courses: one lecturer (LecID) assigned per course
CREATE TABLE IF NOT EXISTS Courses (
    CourseID    VARCHAR(20)  PRIMARY KEY,
    CourseTitle VARCHAR(200) NOT NULL,
    CourseCode  VARCHAR(20)  NOT NULL UNIQUE,
    Description TEXT,
    LecID       VARCHAR(20)  REFERENCES Users(UserID) ON DELETE SET NULL,
    CreatedAt   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Enrolled: student–course many-to-many (students only; lecturer stored in Courses.LecID)
CREATE TABLE IF NOT EXISTS Enrolled (
    UserID     VARCHAR(20) NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    CourseID   VARCHAR(20) NOT NULL REFERENCES Courses(CourseID) ON DELETE CASCADE,
    EnrolledAt TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (UserID, CourseID)
);

-- CalendarEvents: per-course events (assignments deadlines, lectures, etc.)
CREATE TABLE IF NOT EXISTS CalendarEvents (
    EventID     SERIAL      PRIMARY KEY,
    CourseID    VARCHAR(20) NOT NULL REFERENCES Courses(CourseID) ON DELETE CASCADE,
    Title       VARCHAR(200) NOT NULL,
    Description TEXT,
    EventDate   DATE        NOT NULL,
    EventTime   TIME,
    CreatedBy   VARCHAR(20) REFERENCES Users(UserID) ON DELETE SET NULL,
    CreatedAt   TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- Forums: discussion boards attached to a course
CREATE TABLE IF NOT EXISTS Forums (
    ForumID     SERIAL       PRIMARY KEY,
    CourseID    VARCHAR(20)  NOT NULL REFERENCES Courses(CourseID) ON DELETE CASCADE,
    Title       VARCHAR(200) NOT NULL,
    Description TEXT,
    CreatedBy   VARCHAR(20)  REFERENCES Users(UserID) ON DELETE SET NULL,
    CreatedAt   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- DiscussionThreads: topic threads inside a forum
CREATE TABLE IF NOT EXISTS DiscussionThreads (
    ThreadID  SERIAL       PRIMARY KEY,
    ForumID   INTEGER      NOT NULL REFERENCES Forums(ForumID) ON DELETE CASCADE,
    UserID    VARCHAR(20)  REFERENCES Users(UserID) ON DELETE SET NULL,
    Title     VARCHAR(300) NOT NULL,
    Content   TEXT         NOT NULL,
    CreatedAt TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ThreadReplies: nested replies (Reddit-style) via self-referential ParentReplyID
CREATE TABLE IF NOT EXISTS ThreadReplies (
    ReplyID       SERIAL      PRIMARY KEY,
    ThreadID      INTEGER     NOT NULL REFERENCES DiscussionThreads(ThreadID) ON DELETE CASCADE,
    ParentReplyID INTEGER     REFERENCES ThreadReplies(ReplyID) ON DELETE CASCADE,
    UserID        VARCHAR(20) REFERENCES Users(UserID) ON DELETE SET NULL,
    Content       TEXT        NOT NULL,
    CreatedAt     TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ContentSections: named groupings of content within a course
CREATE TABLE IF NOT EXISTS ContentSections (
    SectionID   SERIAL       PRIMARY KEY,
    CourseID    VARCHAR(20)  NOT NULL REFERENCES Courses(CourseID) ON DELETE CASCADE,
    SectionName VARCHAR(200) NOT NULL,
    OrderIndex  INTEGER      NOT NULL DEFAULT 0,
    CreatedAt   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- CourseContent: individual resources (links, files, slides) inside a section
CREATE TABLE IF NOT EXISTS CourseContent (
    ContentID   SERIAL       PRIMARY KEY,
    SectionID   INTEGER      NOT NULL REFERENCES ContentSections(SectionID) ON DELETE CASCADE,
    Title       VARCHAR(200) NOT NULL,
    ContentType VARCHAR(10)  NOT NULL CHECK (ContentType IN ('link', 'file', 'slide')),
    ContentURL  TEXT         NOT NULL,
    Description TEXT,
    CreatedAt   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Assignments: graded work items per course
CREATE TABLE IF NOT EXISTS Assignments (
    AssignmentID SERIAL       PRIMARY KEY,
    CourseID     VARCHAR(20)  NOT NULL REFERENCES Courses(CourseID) ON DELETE CASCADE,
    Title        VARCHAR(200) NOT NULL,
    Description  TEXT,
    DueDate      TIMESTAMP,
    MaxGrade     NUMERIC(6,2) NOT NULL DEFAULT 100 CHECK (MaxGrade > 0),
    CreatedAt    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Submissions: one submission per student per assignment
CREATE TABLE IF NOT EXISTS Submissions (
    SubmissionID SERIAL       PRIMARY KEY,
    AssignmentID INTEGER      NOT NULL REFERENCES Assignments(AssignmentID) ON DELETE CASCADE,
    StudentID    VARCHAR(20)  NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    Content      TEXT         NOT NULL,
    SubmittedAt  TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (AssignmentID, StudentID)
);

-- Grades: one grade per submission; Grade contributes to the student's final average
CREATE TABLE IF NOT EXISTS Grades (
    GradeID      SERIAL      PRIMARY KEY,
    SubmissionID INTEGER     NOT NULL UNIQUE REFERENCES Submissions(SubmissionID) ON DELETE CASCADE,
    Grade        NUMERIC(6,2) NOT NULL CHECK (Grade >= 0),
    GradedBy     VARCHAR(20) REFERENCES Users(UserID) ON DELETE SET NULL,
    GradedAt     TIMESTAMP   NOT NULL DEFAULT NOW()
);
