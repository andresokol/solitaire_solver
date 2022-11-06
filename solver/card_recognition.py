import time

import torch
from PIL import Image
from torch import nn
from torchvision import transforms

from .base import Card


class Network(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Conv2d(3, 3, kernel_size=3, stride=1, padding=1)
        self.norm = nn.BatchNorm2d(3)
        self.relu = nn.ReLU(inplace=True)
        self.flatten = nn.Flatten()

        self.dense = nn.Linear(2592, 1024)

        self.to_suites = nn.Linear(1024, 4)
        self.to_values = nn.Linear(1024, 13)

    def forward(self, x: torch.Tensor):
        out = self.conv(x)
        out = self.norm(out)
        out = self.relu(out)
        out = self.flatten(out)

        out = self.dense(out)

        out_suites = self.to_suites(out)
        out_values = self.to_values(out)

        return out_suites, out_values


def _measure_time(log_function_name: str):
    def wrapper(func: callable):
        def _wrapped(*args):
            start = time.time()
            result = func(*args)
            end = time.time()

            delta_ms = (end - start) * 1000

            print(
                log_function_name,
                f"took: {delta_ms:.2f} ms",
            )
            return result

        return _wrapped

    return wrapper


class CardRecognizer:
    WEIGHTS_PATH = "models/win_card_predictor_weights.pt"
    NETWORK_CLASS = Network

    @_measure_time("Model initialization")
    def __init__(self):
        self.model = self.NETWORK_CLASS()
        self.model.load_state_dict(torch.load(self.WEIGHTS_PATH))
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        )

    @_measure_time("Recognition")
    def recognize(self, img: Image) -> Card:
        cropped = img.crop((0, 0, 24, 36))
        input_tensor = self.transform(cropped)
        input_tensor = torch.unsqueeze(input_tensor, 0)

        pred_suite, pred_value = self.model(input_tensor)

        suite = torch.argmax(pred_suite).item()
        value = torch.argmax(pred_value).item()
        return Card(suite, value)
