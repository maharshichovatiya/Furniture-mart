from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException
from django.conf import settings
from django.utils.html import format_html
from .models import Furniture, UserProfile
from .serializers import FurnitureSerializer
from django.http import JsonResponse
import json
import os
from rest_framework.decorators import api_view
class FurnitureViewSet(viewsets.ModelViewSet): # type: ignore
    queryset = Furniture.objects.all()
    serializer_class = FurnitureSerializer

class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        mobile_no = request.data.get('mobile_no')  # New field
        address = request.data.get('address')        # New field



        # Validate inputs
        if not username or not password or not email or not mobile_no or not address:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=user, mobile_no=mobile_no, address=address)
            user_profile_data = {
                'username': username,
                'email': email,
                'mobile_no': mobile_no,
                'address': address,
            }
            file_path = r'D:\New folder\FurnitureMart\frontend\src\api\profile.json'
            with open(file_path, 'w') as json_file:
                json.dump(user_profile_data, json_file)

            # Prepare the HTML email content
            subject = 'Welcome to FurnitureMart'
            message = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: auto;
                        background: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333;
                        text-align: center;
                    }}
                    h2 {{
                        color: #555;
                        margin-top: 30px;
                    }}
                    p {{
                        color: #555;
                        line-height: 1.6;
                    }}
                    .footer {{
                        margin-top: 40px;
                        text-align: center;
                        font-size: 0.9rem;
                        color: #777;
                    }}
                    .highlight {{
                        color: #dd7210; /* Highlight color */
                        font-weight: bold;
                    }}
                    .testimonial {{
                        border-left: 4px solid #b69271;
                        padding-left: 10px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Welcome to FurnitureMart, {username}!</h1>
                    <p>Thank you for signing up! Your registration was successful.</p>

                    <h2>Why Choose FurnitureMart?</h2>
                    <p>At FurnitureMart, we offer a wide range of high-quality furniture designed to suit your style and needs. Our products are crafted with care, ensuring durability and elegance.</p>

                    <h2>Featured Products</h2>
                    <p>Explore our exclusive collection of:</p>
                    <ul>
                        <li>Modern Sofas</li>
                        <li>Elegant Dining Sets</li>
                        <li>Stylish Bedroom Furniture</li>
                        <li>Outdoor Essentials</li>
                    </ul>

                    <h2>What Our Customers Say</h2>
                    <div class="testimonial">
                        <p>"FurnitureMart transformed my home! The quality is exceptional and the service is top-notch!" - Jane Doe</p>
                    </div>
                    <div class="testimonial">
                        <p>"I love my new dining set! It's perfect for family gatherings." - John Smith</p>
                    </div>

                    <h2>Stay Connected!</h2>
                    <p>Follow us on social media and stay updated with our latest offers:</p>
                    <ul>
                        <li>Facebook</li>
                        <li>Instagram</li>
                        <li>Twitter</li>
                    </ul>

                    <p>If you have any questions, feel free to reach out to us.</p>
                    <div class="footer">
                        <p>Best regards,</p>
                        <p>The FurnitureMart Team</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send confirmation email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],  # Ensure this is a list
                fail_silently=False,
                html_message=message  # Specify the HTML message
            )

            return Response({'success': 'User created successfully. A confirmation email has been sent.'}, status=status.HTTP_201_CREATED)

        except BadHeaderError:
            return Response({'error': 'Invalid header found.'}, status=status.HTTP_400_BAD_REQUEST)
        except SMTPException as e:
            return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Validate inputs
        if not username or not password:
            return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Provide your own token generation logic if needed
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Log out the user
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
    
class CheckoutView(APIView):
   def post(self, request):
        try:
            # Use DRF's request.data to automatically parse JSON
            data = request.data
            user_email = data.get('email')
            name = data.get('name')
            address = data.get('address')
            mobile_no = data.get('totalAmount')

            # Validate the email
            if not user_email:
                return Response({'status': 'error', 'message': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

            html_message = format_html('''\
    <div style="font-family: 'Arial', sans-serif; padding: 20px; max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: #ff6b6b; text-align: center; font-size: 24px; margin-bottom: 20px;">
            Order Confirmation
        </h1>
        <p style="color: #333333; font-size: 16px; line-height: 1.5;">
            Dear <strong>{name}</strong>,<br><br>
            Thank you for your order! We appreciate your business.
        </p>
        <p style="color: #333333; font-size: 16px; line-height: 1.5;">
            <strong>Delivery Details:</strong><br>
            Address: <span style="color: #555555;">{address}</span><br>
            <strong>Total Price:</strong> <span style="color: #555555;">{mobile_no}</span>
        </p>
        <p style="color: #333333; font-size: 16px; line-height: 1.5;">
            We will notify you once your order is shipped. If you have any questions, feel free to contact us.
        </p>
        <p style="color: #777777; font-size: 12px; text-align: center; margin-top: 40px;">
            If you didn't make this order, please ignore this email.
        </p>
    </div>
''', name=name, address=address, mobile_no=mobile_no)


            subject = 'Order Confirmation'
            recipient_list = [user_email]

            # Send email with HTML content
            send_mail(
                subject,
                message='',  # No plain text message
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,  # Send the HTML message
                fail_silently=False
            )

            return Response({'status': 'success', 'message': 'Order confirmation email sent successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)