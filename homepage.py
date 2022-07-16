from django.shortcuts import render, redirect, get_object_or_404

def get_homepage(request):
    return render(request, 'homepage.html')