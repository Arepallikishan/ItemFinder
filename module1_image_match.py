import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load pretrained ResNet18 model (loads only once)
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Remove final classification layer (we only need features)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.eval()

# Image preprocessing (VERY IMPORTANT for accuracy)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def extract_features(image_path):
    """
    Extract deep features from an image using pretrained ResNet18
    """
    # Open image safely and convert to RGB
    image = Image.open(image_path).convert("RGB")

    # Apply preprocessing
    image = transform(image).unsqueeze(0)

    # Disable gradient (faster inference)
    with torch.no_grad():
        features = model(image)

    # Convert tensor to 1D numpy array
    features = features.numpy().flatten()

    return features


def compare_images(image1_path, image2_path):
    """
    Compare two images and return similarity percentage (0 to 100)
    """
    # Extract features from both images
    feat1 = extract_features(image1_path)
    feat2 = extract_features(image2_path)

    # Compute cosine similarity
    similarity = cosine_similarity([feat1], [feat2])[0][0]

    # Convert to percentage
    similarity_percentage = float(similarity * 100)

    return similarity_percentage