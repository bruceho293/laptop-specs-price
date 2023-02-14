from django.shortcuts import render
from rest_framework import status

def error_404_not_found(request, exception):
    error_msg = 'Oops! Cannot find the page you are looking for!'
    return render(request, '404.html', {'error_msg': error_msg}, status=status.HTTP_404_NOT_FOUND)
