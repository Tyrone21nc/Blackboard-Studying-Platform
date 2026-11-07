import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from django.conf import settings
from .models import Course, CourseMaterial, GradeRecord, StudyPlan

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_study_plan_for_course(course_id, target_grade):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return "Course not found."

    materials = course.materials.all()
    grades = course.grades.all()

    materials_text = "\n\n".join([f"--- [{m.material_type.upper()}] {m.title} ---\n{m.text_content}" for m in materials])
    grades_text = "\n".join([f"- {g.assignment_name}: {g.score}/{g.points_possible} (Weight: {g.weight}%, Category: {g.category})" for g in grades])

    prompt = f"""
    You are an expert academic advisor and AI tutor. 
    Analyze the following course information for {course.code}: {course.name}.
    The student's target grade is: {target_grade}.

    CURRENT GRADES RECORDED:
    {grades_text if grades_text else "No grades recorded yet."}

    COURSE MATERIALS & SYLLABUS:
    {materials_text if materials_text else "No materials provided yet."}

    Please provide a comprehensive study plan structured in Markdown:
    1. **Grade Breakdown Analysis**: Calculate what scores the student needs on remaining assignments/exams to secure a {target_grade}.
    2. **Upcoming Exam/Quiz Prep**: Outline a step-by-step preparation plan based on the lectures, notes, and syllabus topics already covered.
    3. **Actionable Weekly Schedule**: Give practical tips on how to study effectively for this specific class.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    plan_text = response.text

    StudyPlan.objects.create(
        course=course,
        target_grade_goal=target_grade,
        plan_content=plan_text
    )

    return plan_text
def get_ai_chat_response(course_id, user_message):
    try:
        course = Course.objects.get(id=course_id)
        materials = course.materials.all()
        grades = course.grades.all()
    except Course.DoesNotExist:
        materials = []
        grades = []

    context = f"Course: {course.code} - {course.name}\n"
    context += "Grades:\n" + "\n".join([f"- {g.assignment_name}: {g.score}/{g.points_possible}" for g in grades]) + "\n\n"
    context += "Materials & Notes:\n" + "\n".join([f"[{m.title}]: {m.text_content[:1500]}" for m in materials])

    prompt = f"""
    You are an intelligent AI study assistant helping a college student with their coursework.
    Use the following course context to answer the student's question accurately. If the answer isn't in the context, use your general knowledge but note it.

    CONTEXT:
    {context}

    STUDENT QUESTION:
    {user_message}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text