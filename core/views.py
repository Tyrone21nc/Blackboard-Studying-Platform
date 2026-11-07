from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, ChatMessage
from .gemini_service import generate_study_plan_for_course, get_ai_chat_response

def dashboard_view(request):
    courses = Course.objects.all().order_by('-updated_at')
    return render(request, 'core/dashboard.html', {'courses': courses})

def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    latest_plan = course.study_plans.order_by('-generated_at').first()
    chat_messages = course.chats.order_by('timestamp')

    if request.method == 'POST' and 'update_target' in request.POST:
        new_target = request.POST.get('target_grade')
        if new_target in ['A', 'B', 'C']:
            course.target_grade = new_target
            course.save()
            generate_study_plan_for_course(course.id, new_target)
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST' and 'chat_message' in request.POST:
        user_msg = request.POST.get('chat_message').strip()
        if user_msg:
            ChatMessage.objects.create(course=course, sender='user', message=user_msg)
            ai_response = get_ai_chat_response(course.id, user_msg)
            ChatMessage.objects.create(course=course, sender='ai', message=ai_response)
        return redirect('course_detail', course_id=course.id)

    context = {
        'course': course,
        'grades': course.grades.all(),
        'materials': course.materials.all(),
        'latest_plan': latest_plan,
        'chat_messages': chat_messages,
    }
    return render(request, 'core/course_detail.html', context)