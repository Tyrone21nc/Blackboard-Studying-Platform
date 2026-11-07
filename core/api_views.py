from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, GradeRecord, CourseMaterial
from .gemini_service import generate_study_plan_for_course

class BlackboardSyncAPIView(APIView):
    def post(self, request):
        data = request.data
        code = data.get('course_code')
        name = data.get('course_name')
        target_grade = data.get('target_grade', 'A')

        if not code or not name:
            return Response({"error": "course_code and course_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        course, created = Course.objects.update_or_create(
            code=code,
            defaults={'name': name, 'target_grade': target_grade}
        )

        grades_data = data.get('grades', [])
        for g in grades_data:
            GradeRecord.objects.update_or_create(
                course=course,
                assignment_name=g.get('assignment_name'),
                defaults={
                    'weight': g.get('weight', 0.0),
                    'score': g.get('score'),
                    'points_possible': g.get('points_possible'),
                    'category': g.get('category', '')
                }
            )

        materials_data = data.get('materials', [])
        for m in materials_data:
            CourseMaterial.objects.create(
                course=course,
                title=m.get('title', 'Untitled'),
                material_type=m.get('material_type', 'other'),
                text_content=m.get('text_content', '')
            )

        try:
            generate_study_plan_for_course(course.id, course.target_grade)
        except Exception as e:
            print(f"Warning: Failed to auto-generate study plan on sync: {e}")

        return Response({"message": f"Successfully synced data for {code}!"}, status=status.HTTP_200_OK)