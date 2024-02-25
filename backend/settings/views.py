from django.http import HttpRequest
from django.shortcuts import render


async def landing(request: HttpRequest):
    return render(request, "landing.html")
