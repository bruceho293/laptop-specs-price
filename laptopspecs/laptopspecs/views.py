from django.shortcuts import render

def error_404_not_found(request, exception):
    error_msg = 'Oops! Cannot find the page you are looking for!'
    return render(request, '404.html', {'error_msg': error_msg})
