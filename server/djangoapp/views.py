# Uncomment the required imports before adding the code

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from datetime import datetime
import logging
import json
import traceback

from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Logger instance
logger = logging.getLogger(__name__)


# ---------------- AUTH VIEWS ---------------- #

@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"}, status=200)
        else:
            return JsonResponse({"error": "Invalid Credentials"}, status=401)
    except Exception as e:
        logger.error(f"Login error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


def logout_request(request):
    logout(request)  # Terminate user session
    return JsonResponse({"userName": ""}, status=200)


@csrf_exempt
@require_POST
def registration(request):
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username, "error": "Already Registered"}, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"}, status=201)

    except Exception as e:
        logger.error(f"Registration error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)


# ---------------- DEALERSHIPS ---------------- #

def get_dealerships(request, state=None):
    try:
        endpoint = "/fetchDealers" if not state else f"/fetchDealers/{state}"
        dealerships = get_request(endpoint)
        return JsonResponse({"dealers": dealerships}, status=200)
    except Exception as e:
        logger.error(f"Get dealerships error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Failed to fetch dealerships"}, status=500)


def get_dealer_details(request, dealer_id):
    try:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"dealer": dealership}, status=200)
    except Exception as e:
        logger.error(f"Get dealer details error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Failed to fetch dealer details"}, status=500)


def get_dealer_reviews(request, dealer_id):
    try:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)

        for review in reviews:
            sentiment_response = analyze_review_sentiments(review.get("review", ""))
            review["sentiment"] = (
                sentiment_response.get("sentiment")
                if sentiment_response and "sentiment" in sentiment_response
                else "unknown"
            )

        return JsonResponse({"reviews": reviews}, status=200)

    except Exception as e:
        logger.error(f"Get dealer reviews error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Failed to fetch dealer reviews"}, status=500)


# ---------------- REVIEWS ---------------- #

@csrf_exempt
@require_POST
def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        response = post_review(data)
        return JsonResponse({"status": "success", "response": response}, status=200)
    except Exception as e:
        logger.error(f"Add review error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Error in posting review"}, status=500)


# ---------------- CARS ---------------- #

def get_cars(request):
    try:
        count = CarMake.objects.count()
        if count == 0:
            initiate()  # Populate cars if empty

        car_models = CarModel.objects.select_related("car_make")
        cars = [{"CarModel": cm.name, "CarMake": cm.car_make.name} for cm in car_models]

        return JsonResponse({"CarModels": cars}, status=200)
    except Exception as e:
        logger.error(f"Get cars error: {e}\n{traceback.format_exc()}")
        return JsonResponse({"error": "Failed to fetch cars"}, status=500)
