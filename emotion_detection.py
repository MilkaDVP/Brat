import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
import cv2
from PIL import Image

# Define the Emotic model architecture
class Emotic(nn.Module):
    def __init__(self, num_context_features, num_body_features):
        super(Emotic, self).__init__()
        self.num_context_features = num_context_features
        self.num_body_features = num_body_features
        self.fc1 = nn.Linear((self.num_context_features + num_body_features), 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.d1 = nn.Dropout(p=0.5)
        self.fc_cat = nn.Linear(256, 26)  # 26 discrete emotion categories
        self.fc_cont = nn.Linear(256, 3)   # 3 continuous dimensions
        self.relu = nn.ReLU()

    def forward(self, x_context, x_body):
        context_features = x_context.view(-1, self.num_context_features)
        body_features = x_body.view(-1, self.num_body_features)
        fuse_features = torch.cat((context_features, body_features), 1)
        fuse_out = self.fc1(fuse_features)
        fuse_out = self.bn1(fuse_out)
        fuse_out = self.relu(fuse_out)
        fuse_out = self.d1(fuse_out)
        cat_out = self.fc_cat(fuse_out)
        cont_out = self.fc_cont(fuse_out)
        return cat_out, cont_out

class EmotionDetector:
    def __init__(self):
        # Initialize models
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load body model (ResNet)
        self.body_model = torch.load('models/model_body1.pth', map_location=self.device)
        self.body_model.to(self.device)
        self.body_model.eval()

        # Load context model (ResNet)
        self.context_model = torch.load('models/model_context1.pth', map_location=self.device)
        self.context_model.to(self.device)
        self.context_model.eval()

        # Load Emotic model
        self.emotic_model = torch.load('models/model_emotic1.pth', map_location=self.device)
        self.emotic_model.to(self.device)
        self.emotic_model.eval()

        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

        # Define image transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Emotion categories
        self.cat_emotions = ['Affection', 'Anger', 'Annoyance', 'Anticipation', 'Aversion',
                           'Confidence', 'Disapproval', 'Disconnection', 'Disquietment',
                           'Doubt/Confusion', 'Embarrassment', 'Engagement', 'Esteem',
                           'Excitement', 'Fatigue', 'Fear', 'Happiness', 'Pain',
                           'Peace', 'Pleasure', 'Sadness', 'Sensitivity', 'Suffering',
                           'Surprise', 'Sympathy', 'Yearning']

    def preprocess_image(self, image):
        """Convert OpenCV image to PIL and apply transforms"""
        if isinstance(image, np.ndarray):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        return self.transform(image).unsqueeze(0)

    def detect_person(self, frame):
        """Detect person in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Try to detect full body first
        bodies = self.body_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(bodies) > 0:
            return bodies[0]  # Return first detected body
        
        # If no body detected, try to detect face and expand region
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Expand face region to approximate body region
            x, y, w, h = faces[0]
            body_h = int(h * 4)  # Approximate body height
            body_w = int(w * 1.5)  # Approximate body width
            body_x = max(0, x - int(w * 0.25))
            body_y = min(frame.shape[0], y + h)  # Start from bottom of face
            
            return (body_x, body_y, body_w, body_h)
            
        return None

    def detect_emotions(self, frame):
        """Detect emotions in a video frame"""
        with torch.no_grad():
            # Preprocess frame
            body_tensor = self.preprocess_image(frame).to(self.device)
            context_tensor = body_tensor  # Using same frame for context for simplicity

            # Extract features
            body_features = self.body_model(body_tensor)
            context_features = self.context_model(context_tensor)

            # Get emotion predictions
            cat_out, cont_out = self.emotic_model(context_features, body_features)
            
            # Convert to probabilities
            cat_prob = torch.sigmoid(cat_out).cpu().numpy()[0]
            cont_vals = cont_out.cpu().numpy()[0]

            # Get top emotions
            top_emotions = []
            for i in range(len(self.cat_emotions)):
                if cat_prob[i] > 0.5:  # Threshold for emotion detection
                    top_emotions.append((self.cat_emotions[i], float(cat_prob[i])))
            
            top_emotions.sort(key=lambda x: x[1], reverse=True)

            return top_emotions, cont_vals

    def draw_results(self, frame, bbox, emotions, dimensions):
        """Draw bounding box and emotions"""
        if bbox is None:
            return
        
        x, y, w, h = bbox
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Calculate text positions
        text_x = x + 10
        text_y = y + 30
        
        # Draw valence value on top of box
        val_text = f"Valence: {dimensions[0]:.2f}"
        cv2.putText(frame, val_text, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw top 5 emotions inside box
        for emotion, prob in emotions[:5]:
            text = f"{emotion}: {prob:.2f}"
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            text_y += 20

def main():
    # Initialize video capture
    cap = cv2.VideoCapture(1)
    detector = EmotionDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect person
        bbox = detector.detect_person(frame)
        
        # Detect emotions
        emotions, dimensions = detector.detect_emotions(frame)

        # Draw results
        detector.draw_results(frame, bbox, emotions, dimensions)

        # Display frame
        cv2.imshow('Emotion Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
