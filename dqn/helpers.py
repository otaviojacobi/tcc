import torch

import torchvision.transforms as T
from PIL import Image


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

img_to_tensor = T.Compose([
                    T.ToPILImage(),
                    T.Grayscale(num_output_channels=1),
                    T.Resize((110, 84), interpolation=Image.NEAREST),
                    T.ToTensor()
                ])

def preprocess_image(img):
    return  img_to_tensor(img)[:, 18:102, :].to(device)

def shift_tensor(tensor, x):
    return torch.cat((tensor[1:], x))