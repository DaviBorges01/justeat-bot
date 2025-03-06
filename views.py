import requests
import json
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import User

# Configurações da API do SkipTheDishes
API_BASE_URL = "https://api-courier-produk.skipthedishes.com"
APP_TOKEN = "377f3398-38b8-42e7-873b-378023ca3cab"

# Função para obter credenciais do usuário no banco de dados
def get_user_credentials(user):
    return user.email, user.password  # Altere conforme o modelo de usuário

# Função para converter timestamp epoch
def epoch_conv(epoch):
    epoch = epoch / 1000.0
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(epoch))

# Login na API do SkipTheDishes
def login_to_skip(email, password):
    url = f"{API_BASE_URL}/v4/couriers/two-fa-login"
    headers = {
        "accept": "application/json",
        "app-token": APP_TOKEN,
        "content-type": "text/plain;charset=UTF-8",
    }
    data = json.dumps({"email": email, "password": password})
    response = requests.post(url, headers=headers, data=data)
    return response.json() if response.status_code == 200 else None

# Obter shifts disponíveis e agendados
def get_shifts(user_token, user_id):
    url = f"{API_BASE_URL}/v2/couriers/{user_id}/shifts/scheduled"
    params = {"includeAvailable": "true", "timezone": "Europe/London"}
    headers = {"app-token": APP_TOKEN, "user-token": user_token}
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None

# Automatizar reserva de shifts
def book_shift(user_token, shift_id):
    url = f"{API_BASE_URL}/v2/couriers/shifts/{shift_id}/book"
    headers = {"app-token": APP_TOKEN, "user-token": user_token}
    response = requests.post(url, headers=headers)
    return response.json() if response.status_code == 200 else {"error": "Falha ao reservar shift"}

@login_required
def index(request):
    email, password = get_user_credentials(request.user)
    login_response = login_to_skip(email, password)
    if not login_response:
        return JsonResponse({"error": "Login falhou"})
    
    user_token = login_response.get("token")
    user_id = login_response.get("id")
    shifts_data = get_shifts(user_token, user_id)
    
    if not shifts_data:
        return JsonResponse({"error": "Não foi possível buscar os shifts"})
    
    available_shifts = [
        {
            "start": epoch_conv(shift["shiftTime"]["start"]),
            "end": epoch_conv(shift["shiftTime"]["end"]),
            "shift_id": shift["id"]
        }
        for shift in shifts_data.get("availableShifts", [])
    ]
    
    for shift in available_shifts:
        book_shift(user_token, shift["shift_id"])
        time.sleep(1)  # Evitar múltiplas requisições seguidas
    
    return render(request, "index.html", {"availableShifts": available_shifts})
