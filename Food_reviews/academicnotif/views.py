from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *
from .users import*
from .utils import predict_sentiment
import os
from django.conf import settings
from tabula import read_pdf
import pandas as pd
from openpyxl import Workbook
from django.http import HttpResponse
from pymongo import MongoClient
from pandas import ExcelWriter
import gridfs
from django.shortcuts import render
from .models import UserFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
#from .utils import predict_sentiment
client = MongoClient('mongodb://localhost:27017')  # Replace with your MongoDB connection string
db = client['your_database_name']  # Replace with your MongoDB database name
fs = gridfs.GridFS(db)
def home(request):
    username = request.session.get('username') 
    firstname=request.session.get('first_name')
    lastname=request.session.get('last_name')
    return render(request, 'home.html', {'username': username, 'firstname':firstname})
from django.contrib.auth.hashers import check_password
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects(username=username).first()
            if user and check_password(password, user.password):
                # Manually set session
                request.session['username'] = user.username
                messages.success(request, f"Hi {user.first_name.title()}, welcome back!")
                return redirect('home')
            
        messages.error(request, "Invalid username or password")
        return render(request, 'login', {'form': form})
from .models import RegisterForm
from .models import User
from django.contrib.auth.hashers import make_password
def register_view(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register', {'form': form})

    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects(username=username).first():
                messages.error(request, "Username already exists")
                return render(request, 'register', {'form': form})
            
            user = User(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=username,
                password=make_password(form.cleaned_data['password'])
            )
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')

        return render(request, 'register', {'form': form})
from io import BytesIO
def post_view(request):
    uploaded_files = []  # Initialize the list to store uploaded file names

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Store the uploaded file in MongoDB
        file_id = fs.put(uploaded_file.read(), filename=uploaded_file.name)
        
        # Add the filename to the list (you can choose to store these in MongoDB for persistence)
        uploaded_files.append(uploaded_file.name)
        
        try:
            # Read the Excel file content (after fetching from MongoDB GridFS)
            file_data = fs.get(file_id)
            df = pd.read_excel(file_data, engine='openpyxl')
            
            # Ensure the Excel file contains a column for reviews
            if 'Reviews' not in df.columns:
                return JsonResponse({'error': 'Excel file must contain a "review" column'}, status=400)

            # Perform sentiment analysis on each review
            results = []
            for index, row in df.iterrows():
                review = row['Reviews']
                sentiment = predict_sentiment(review)
                results.append({
                    'review': review,
                    'sentiment': sentiment
                })

            # Create a new DataFrame with results
            results_df = pd.DataFrame(results)

            # Save the results as an Excel file
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_results.xlsx"'
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Results')

            return response  # This will trigger the download of the new Excel file

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Retrieve all the uploaded file names from MongoDB (this could be done by querying the 'files' collection)
    files_cursor = fs.find()
    uploaded_files = [file.filename for file in files_cursor]

    return render(request, 'post', {'uploaded_files': uploaded_files})
from django.shortcuts import get_object_or_404, redirect
from pymongo.errors import PyMongoError
def delete_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        
        if file_name:
            # Fetch the file from MongoDB GridFS
            file = fs.find_one({'filename': file_name})
            if file:
                try:
                    # Delete the file from MongoDB
                    fs.delete(file._id)  # Use the _id property of GridFS file object
                    # Redirect back to the post view to refresh the page
                    return redirect('post')  # Replace 'post' with the correct URL name for your page
                except PyMongoError as e:
                    return JsonResponse({'error': f'Error deleting file: {str(e)}'}, status=500)
            else:
                return JsonResponse({'error': 'File not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def logout_view(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('login') 
from django.http import JsonResponse
def download_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')

        if file_name:
            # Fetch the file from MongoDB GridFS
            file = fs.find_one({'filename': file_name})
            if file:
                # Prepare the file for download
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
                return response
            else:
                return HttpResponse("File not found", status=404)

    return redirect('post') 


def analyze(request):
    """
    Handles both GET and POST requests to analyze sentiment.
    On POST, predicts the sentiment of the provided review text.
    """
    if request.method == "POST":
        # Get the review text from the submitted form
        review = request.POST.get('review', '')
        sentiment = predict_sentiment(review)  # Predict sentiment using the utility function
        return render(request, 'analyze', {'sentiment': sentiment, 'review': review})

    # Render the form for GET requests
    return render(request, 'analyze')
def result(request):
     return render(request, 'result')
def work(request):
    return render(request, 'workinprogress')


