
import streamlit as st

from modules.profile import extract_resume_text, analyze_resume

from database import (
    initialize_database,
    fix_application_database,
    save_profile as db_save_profile,
    get_latest_profile,
    save_skill_gap,
    save_roadmap,
    save_interview,
    save_application,
    get_applications,
    update_application_record,
    fix_interview_database
)

from modules.skill_gap import analyze_skill_gap
from modules.roadmap import generate_roadmap
from modules.projects import generate_projects
from modules.interview import (
    generate_interview_question,
    evaluate_answer
)
from modules.applications import (
    create_application,
    update_application,
    analyze_application_patterns
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide"
)

initialize_database()
fix_application_database()
fix_interview_database()

st.title("🚀 CareerPilot AI")
st.caption("Your AI-powered career development assistant.")


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "profile": None,
    "profile_id": None,
    "skill_gap": None,
    "roadmap": None,
    "projects": None,
    "question": None,
    "interview_history": [],
    "completed_tasks": [],
    "applications": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Load saved profile and applications
if st.session_state.profile is None:

    saved = get_latest_profile()

    if saved:
        st.session_state.profile_id = saved["id"]
        st.session_state.profile = saved["profile"]

        st.session_state.applications = get_applications(
            saved["id"]
        )


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🚀 CareerPilot AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Resume Analyzer",
        "Skill Gap Analysis",
        "Learning Roadmap",
        "Portfolio Projects",
        "Mock Interview",
        "Application Tracker"
    ]
)

target_role = st.sidebar.text_input(
    "Target Job Role",
    value="Machine Learning Engineer"
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.header("Your Career Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Resume Status",
        "Uploaded" if st.session_state.profile else "Not uploaded"
    )

    col2.metric(
        "Skill Gap Analysis",
        "Completed" if st.session_state.skill_gap else "Pending"
    )

    col3.metric(
        "Applications",
        len(st.session_state.applications)
    )

    st.divider()

    st.subheader("Your Career Journey")

    steps = [
        ("1. Resume Analysis", st.session_state.profile),
        ("2. Skill Gap Analysis", st.session_state.skill_gap),
        ("3. Learning Roadmap", st.session_state.roadmap),
        ("4. Portfolio Projects", st.session_state.projects)
    ]

    for label, completed in steps:

        status = "✅" if completed else "⏳"
        st.write(f"{status} {label}")

    st.divider()

    st.subheader("📊 Learning Progress")

    if st.session_state.roadmap:

        all_tasks = [
            f"Week {week.get('week')}: {task}"
            for week in st.session_state.roadmap.get("roadmap", [])
            for task in week.get("tasks", [])
        ]

        total_tasks = len(all_tasks)

        completed_count = sum(
            1 for task in all_tasks
            if task in st.session_state.completed_tasks
        )

        if total_tasks > 0:

            progress = completed_count / total_tasks

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Tasks", total_tasks)
            col2.metric("Completed", completed_count)
            col3.metric(
                "Remaining",
                total_tasks - completed_count
            )

            st.progress(progress)

            st.write(
                f"**{progress * 100:.1f}% completed**"
            )

        else:
            st.info("Your roadmap currently has no tasks.")

    else:
        st.info(
            "Generate a learning roadmap to start tracking progress."
        )


# ==================================================
# RESUME ANALYZER
# ==================================================

elif page == "Resume Analyzer":

    st.header("📄 Resume Analyzer")

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Analyze My Resume", type="primary"):

            try:

                with st.spinner(
                    "Reading and analyzing your resume..."
                ):

                    resume_text = extract_resume_text(uploaded_file)

                    if not resume_text.strip():
                        st.error(
                            "No readable text found in this PDF."
                        )
                        st.stop()

                    profile = analyze_resume(resume_text)

                    profile_id = db_save_profile(
                        profile.get("name", "Candidate"),
                        profile
                    )

                    st.session_state.profile = profile
                    st.session_state.profile_id = profile_id

                    # Reset analyses belonging to the old profile
                    st.session_state.skill_gap = None
                    st.session_state.roadmap = None
                    st.session_state.projects = None
                    st.session_state.completed_tasks = []
                    st.session_state.interview_history = []

                st.success("Resume analyzed successfully!")

            except Exception as e:

                st.error(f"Analysis failed: {e}")

    if st.session_state.profile:

        st.subheader("Extracted Candidate Profile")

        st.json(st.session_state.profile)


# ==================================================
# SKILL GAP ANALYSIS
# ==================================================

elif page == "Skill Gap Analysis":

    st.header("🎯 Skill Gap Analysis")

    st.write(
        "Compare your current skills with a real job description."
    )

    job_description = st.text_area(
        "Paste the job description here",
        height=220,
        placeholder="Paste the requirements and responsibilities from a job listing..."
    )

    if st.button("Analyze Skill Gap", type="primary"):

        if not st.session_state.profile:

            st.warning("Analyze your resume first.")

        elif not job_description.strip():

            st.warning("Please enter a job description.")

        else:

            try:

                with st.spinner(
                    "Comparing your skills with the job requirements..."
                ):

                    result = analyze_skill_gap(
                        st.session_state.profile,
                        target_role,
                        job_description
                    )

                    st.session_state.skill_gap = result

                    # Previous roadmap is based on the old skill gap
                    st.session_state.roadmap = None
                    st.session_state.completed_tasks = []

                    if st.session_state.profile_id:

                        save_skill_gap(
                            st.session_state.profile_id,
                            target_role,
                            result
                        )

                st.success("Skill gap analysis complete!")

            except Exception as e:

                st.error(f"Analysis failed: {e}")

    if st.session_state.skill_gap:

        result = st.session_state.skill_gap

        st.divider()

        st.subheader("Your Skill Match")

        st.metric(
            "Match Percentage",
            f"{result.get('match_percentage', 0)}%"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Matched Skills")

            st.write(
                result.get("matched_skills", [])
            )

        with col2:

            st.subheader("Missing Skills")

            st.write(
                result.get("missing_skills", [])
            )

        st.subheader("Partially Matched Skills")

        st.write(
            result.get("partially_matched_skills", [])
        )

        st.subheader("Priority Skills to Learn")

        st.write(
            result.get("priority_skills", [])
        )

        st.write(
            result.get("analysis", "")
        )


# ==================================================
# LEARNING ROADMAP
# ==================================================

elif page == "Learning Roadmap":

    st.header("🗺️ Personalized Learning Roadmap")

    duration = st.selectbox(
        "Roadmap Duration",
        [4, 8, 12, 16, 24],
        index=2,
        format_func=lambda x: f"{x} Weeks"
    )

    if st.button("Generate My Roadmap", type="primary"):

        if not st.session_state.profile:

            st.warning("Analyze your resume first.")

        elif not st.session_state.skill_gap:

            st.warning("Complete skill gap analysis first.")

        else:

            try:

                with st.spinner(
                    "Building your adaptive learning roadmap..."
                ):

                    result = generate_roadmap(
                        st.session_state.profile,
                        st.session_state.skill_gap,
                        target_role,
                        duration_weeks=duration,
                        interview_history=st.session_state.interview_history,
                        completed_tasks=st.session_state.completed_tasks
                    )

                    st.session_state.roadmap = result

                    if st.session_state.profile_id:

                        save_roadmap(
                            st.session_state.profile_id,
                            result
                        )

                st.success("Adaptive roadmap generated!")

            except Exception as e:

                st.error(f"Generation failed: {e}")

    if st.session_state.roadmap:

        roadmap = st.session_state.roadmap

        st.divider()

        st.subheader(
            "🧠 CareerPilot's Adaptation Analysis"
        )

        st.write(
            roadmap.get(
                "adaptation_summary",
                "Roadmap based on your current skill gaps and interview performance."
            )
        )

        st.divider()

        st.subheader("📚 Weekly Learning Plan")

        for week in roadmap.get("roadmap", []):

            week_number = week.get("week")

            with st.expander(
                f"Week {week_number} - {week.get('focus', 'Learning')}"
            ):

                st.write("**Skills:**")

                st.write(
                    week.get("skills", [])
                )

                st.write("**Tasks:**")

                for index, task in enumerate(
                    week.get("tasks", [])
                ):

                    task_id = f"Week {week_number}: {task}"

                    completed = st.checkbox(
                        task,
                        value=task_id in st.session_state.completed_tasks,
                        key=f"task_{week_number}_{index}"
                    )

                    if (
                        completed
                        and task_id not in st.session_state.completed_tasks
                    ):

                        st.session_state.completed_tasks.append(
                            task_id
                        )

                    elif (
                        not completed
                        and task_id in st.session_state.completed_tasks
                    ):

                        st.session_state.completed_tasks.remove(
                            task_id
                        )

                st.write("**Weekly Deliverable:**")

                st.write(
                    week.get("deliverable", "")
                )

                if week.get("reason"):

                    st.write("**Why this week matters:**")

                    st.write(week["reason"])

        st.divider()

        st.subheader("📊 Roadmap Completion")

        all_tasks = [
            f"Week {week.get('week')}: {task}"
            for week in roadmap.get("roadmap", [])
            for task in week.get("tasks", [])
        ]

        total_tasks = len(all_tasks)

        completed_count = sum(
            1 for task in all_tasks
            if task in st.session_state.completed_tasks
        )

        if total_tasks > 0:

            progress = completed_count / total_tasks

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Tasks", total_tasks)
            col2.metric("Completed", completed_count)
            col3.metric(
                "Remaining",
                total_tasks - completed_count
            )

            st.progress(progress)

            st.write(
                f"**{progress * 100:.1f}% completed**"
            )


# ==================================================
# PORTFOLIO PROJECTS
# ==================================================

elif page == "Portfolio Projects":

    st.header("💻 Portfolio Project Recommendations")

    if st.button("Generate Projects", type="primary"):

        if not st.session_state.profile:

            st.warning("Analyze your resume first.")

        elif not st.session_state.skill_gap:

            st.warning("Complete skill gap analysis first.")

        else:

            try:

                with st.spinner(
                    "Finding projects for your skill gaps..."
                ):

                    result = generate_projects(
                        st.session_state.profile,
                        st.session_state.skill_gap,
                        target_role
                    )

                    st.session_state.projects = result

                st.success("Projects generated!")

            except Exception as e:

                st.error(f"Generation failed: {e}")

    if st.session_state.projects:

        for project in st.session_state.projects.get(
            "projects", []
        ):

            with st.expander(
                project.get("title", "Project")
            ):

                st.write(
                    "**Difficulty:**",
                    project.get("difficulty")
                )

                st.write(
                    "**Problem:**",
                    project.get("problem_statement")
                )

                st.write("**Technologies:**")

                st.write(
                    project.get("technologies", [])
                )

                st.write("**Skills Covered:**")

                st.write(
                    project.get("skills_covered", [])
                )

                st.write("**Key Features:**")

                st.write(
                    project.get("key_features", [])
                )

                st.write("**Expected Outcome:**")

                st.write(
                    project.get("expected_outcome", "")
                )


# ==================================================
# MOCK INTERVIEW
# ==================================================

elif page == "Mock Interview":

    st.header("🎤 AI Mock Interview")

    difficulty = st.selectbox(
        "Interview Difficulty",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button(
        "Generate Interview Question",
        type="primary"
    ):

        try:

            with st.spinner(
                "Preparing your interview question..."
            ):

                previous = [
                    item["question"]
                    for item in st.session_state.interview_history
                ]

                st.session_state.question = generate_interview_question(
                    target_role,
                    difficulty,
                    previous
                )

        except Exception as e:

            st.error(
                f"Could not generate question: {e}"
            )

    if st.session_state.question:

        question = st.session_state.question

        st.divider()

        st.subheader(
            question.get("question", "Interview Question")
        )

        st.caption(
            f"Topic: {question.get('topic')} | "
            f"Difficulty: {question.get('difficulty')}"
        )

        answer = st.text_area(
            "Your Answer",
            height=180,
            key="interview_answer"
        )

        if st.button("Evaluate My Answer"):

            if not answer.strip():

                st.warning("Write your answer first.")

            else:

                try:

                    with st.spinner(
                        "Evaluating your answer..."
                    ):

                        evaluation = evaluate_answer(
                            question.get("question"),
                            answer,
                            target_role
                        )

                        interview_record = {
                            "question": question.get("question"),
                            "answer": answer,
                            "evaluation": evaluation
                        }

                        st.session_state.interview_history.append(
                            interview_record
                        )

                        if st.session_state.profile_id:

                            save_interview(
                                st.session_state.profile_id,
                                question.get("question"),
                                answer,
                                evaluation
                            )

                    st.success("Evaluation complete!")

                except Exception as e:

                    st.error(
                        f"Evaluation failed: {e}"
                    )

    if st.session_state.interview_history:

        st.divider()

        st.subheader("Interview Feedback")

        latest = st.session_state.interview_history[-1]

        evaluation = latest["evaluation"]

        st.metric(
            "Overall Score",
            f"{evaluation.get('score', 0)}/10"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Technical Accuracy",
            f"{evaluation.get('technical_accuracy', 0)}/10"
        )

        col2.metric(
            "Clarity",
            f"{evaluation.get('clarity', 0)}/10"
        )

        col3.metric(
            "Relevance",
            f"{evaluation.get('relevance', 0)}/10"
        )

        st.write("**Strengths:**")

        st.write(
            evaluation.get("strengths", [])
        )

        st.write("**Areas to Improve:**")

        st.write(
            evaluation.get("improvements", [])
        )

        st.write("**Suggested Answer:**")

        st.write(
            evaluation.get("ideal_answer", "")
        )


# ==================================================
# APPLICATION TRACKER
# ==================================================

elif page == "Application Tracker":

    st.header("📊 Job Application Tracker")

    if not st.session_state.profile_id:

        st.warning(
            "Analyze your resume first to connect applications to your profile."
        )

    else:

        with st.form("application_form"):

            company = st.text_input("Company Name")

            role = st.text_input("Job Role")

            job_url = st.text_input("Job Listing URL")

            notes = st.text_area("Notes")

            submitted = st.form_submit_button(
                "Add Application"
            )

            if submitted:

                if company.strip() and role.strip():

                    application = create_application(
                        company,
                        role,
                        job_url,
                        notes=notes
                    )

                    save_application(
                        st.session_state.profile_id,
                        application
                    )

                    st.session_state.applications.append(
                        application
                    )

                    st.success(
                        "Application saved permanently!"
                    )

                else:

                    st.warning(
                        "Enter the company and job role."
                    )

        st.divider()

        applications = st.session_state.applications

        if applications:

            st.subheader("Your Applications")

            for index, application in enumerate(applications):

                with st.expander(
                    f"{application['company']} - {application['role']}"
                ):

                    st.write(
                        "Applied:",
                        application.get("applied_date", "")
                    )

                    if application.get("job_url"):

                        st.write(
                            "Job URL:",
                            application["job_url"]
                        )

                    statuses = [
                        "Applied",
                        "Under Review",
                        "Interview",
                        "Rejected",
                        "Offer"
                    ]

                    current_status = application.get(
                        "status", "Applied"
                    )

                    status_index = (
                        statuses.index(current_status)
                        if current_status in statuses
                        else 0
                    )

                    new_status = st.selectbox(
                        "Application Status",
                        statuses,
                        index=status_index,
                        key=f"status_{index}"
                    )

                    responses = [
                        "Pending",
                        "Received"
                    ]

                    current_response = application.get(
                        "response", "Pending"
                    )

                    response_index = (
                        responses.index(current_response)
                        if current_response in responses
                        else 0
                    )

                    new_response = st.selectbox(
                        "Response",
                        responses,
                        index=response_index,
                        key=f"response_{index}"
                    )

                    new_notes = st.text_area(
                        "Update Notes",
                        value=application.get("notes", ""),
                        key=f"notes_{index}"
                    )

                    if st.button(
                        "Save Changes",
                        key=f"save_{index}"
                    ):

                        update_application(
                            application,
                            status=new_status,
                            response=new_response,
                            notes=new_notes
                        )

                        update_application_record(
                            application["company"],
                            application["role"],
                            new_status,
                            new_response,
                            new_notes
                        )

                        st.success(
                            "Application updated!"
                        )

                        st.rerun()

            stats = analyze_application_patterns(
                applications
            )

            st.divider()

            st.subheader("Application Insights")

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Applications",
                stats["total_applications"]
            )

            col2.metric(
                "Response Rate",
                f"{stats['response_rate']}%"
            )

            st.write(
                stats["message"]
            )

        else:

            st.info(
                "Your job applications will appear here."
            )
