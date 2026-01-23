import os
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

# Try to import TensorFlow, else fallback to mock
try:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image as keras_image
    TF_AVAILABLE = True
    # Load model once at startup to save time (mock production behavior)
    # Warning: This downloads 14MB model on first run.
    model = MobileNetV2(weights='imagenet')
except ImportError:
    TF_AVAILABLE = False
    model = None

class AnalyzeDamageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"error": "No image uploaded"}, status=400)

        # Save generic file temporarily
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_upload.jpg')
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        diagnosis = "Unknown Issue"
        price_range = "Check with Mechanic"

        if TF_AVAILABLE and model:
            try:
                # Preprocess
                img = keras_image.load_img(temp_path, target_size=(224, 224))
                x = keras_image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                # Predict
                preds = model.predict(x)
                decoded = decode_predictions(preds, top=3)[0]
                # decoded looks like: [('n02504458', 'walking_stick', 0.8), ...]
                
                # Check for tire related keywords
                labels = [item[1].lower() for item in decoded]
                
                # Simple Logic as requested
                tire_keywords = ['tire', 'wheel', 'sports_car', 'racer', 'car_wheel']
                if any(k in val for val in labels for k in tire_keywords):
                    diagnosis = "Lỗi: Thủng lốp / Mòn lốp"
                    price_range = "50k - 150k VNĐ"
                else:
                    diagnosis = f"Có thể là lỗi vỏ xe hoặc không xác định ({labels[0]})"
                    price_range = "Cần kiểm tra trực tiếp"

            except Exception as e:
                diagnosis = f"AI Error: {str(e)}"
        else:
            # Fallback Mock Logic if TF not installed
            # Check filename or just random default for MVP demo
            diagnosis = "Lỗi: Thủng lốp (Mock logic - AI n/a)"
            price_range = "50k VNĐ"

        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return Response({
            "diagnosis": diagnosis,
            "estimated_price": price_range,
            "technical_details": labels if 'labels' in locals() else "Mock"
        })
