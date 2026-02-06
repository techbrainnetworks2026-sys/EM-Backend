from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsManager

class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        today = timezone.localtime().date()
        
        # Check if already checked in
        attendance, created = Attendance.objects.get_or_create(employee=request.user, date=today)
        
        if attendance.check_in:
            return Response({'error': 'You have already checked in today.'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.check_in = timezone.localtime().time()
        attendance.save()
        
        return Response({
            'message': 'Checked in successfully.',
            'time': attendance.check_in.strftime('%H:%M:%S')
        })

class CheckOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        today = timezone.localtime().date()
        
        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
        except Attendance.DoesNotExist:
            return Response({'error': 'You have not checked in today.'}, status=status.HTTP_400_BAD_REQUEST)

        if attendance.check_out:
            return Response({'error': 'You have already checked out today.'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.check_out = timezone.localtime().time()
        attendance.save()
        
        return Response({
            'message': 'Checked out successfully.',
            'time': attendance.check_out.strftime('%H:%M:%S')
        })

class AttendanceHistoryView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attendance.objects.filter(employee=self.request.user).order_by('-date')

class TodaysAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localtime().date()
        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
            serializer = AttendanceSerializer(attendance)
            return Response(serializer.data)
        except Attendance.DoesNotExist:
             return Response({}) # No record yet
        
class ManagerTodayAttendanceView(generics.ListAPIView):
    """
    Manager can view today's attendance of all employees
    """
    serializer_class = AttendanceSerializer
    permission_classes = [IsManager]   # Only manager allowed

    def get_queryset(self):
        today = timezone.now().date()
        return Attendance.objects.filter(date=today).select_related('employee')
