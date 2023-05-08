"""
Global Configuration
"""
import datetime

# Credentials for Telegram App
credentials = {
    "api_id": 23867482,
    "api_hash": "7c99e3fd9ecfd7b8a4a0374436a046a9",
    "phone": "+38631882318",
    "username": "",
}

"""s
Data Location
"""
# Path to folder for storing/loading raw data --- scraped messages
raw_data_path = "./Data/Messages/RawData"
# Path to folder for loading csv with chat/channel names
chat_data_path = "Data/ChatIDLists"
# Path to store graphml files
graph_data_path = "Data/Graphs"
# Path to folder with models
model_data_path = "Data/Models"

"""
Intervals over witch to perform data collection
"""
epochs = {
    "Epoch 1": [
        datetime.datetime.strptime("18.10.2016 00:00:00", "%d.%m.%Y %H:%M:%S"),
        datetime.datetime.strptime("25.11.2018 00:00:00", "%d.%m.%Y %H:%M:%S"),
    ],
    "Epoch 2": [
        datetime.datetime.strptime("25.11.2018 00:00:00", "%d.%m.%Y %H:%M:%S"),
        datetime.datetime.strptime("31.12.2020 00:00:00", "%d.%m.%Y %H:%M:%S"),
    ],
    "Epoch 3": [
        datetime.datetime.strptime("31.12.2020 00:00:00", "%d.%m.%Y %H:%M:%S"),
        datetime.datetime.strptime("07.02.2023 00:00:00", "%d.%m.%Y %H:%M:%S"),
    ],
}


"""
Parameters to determine sampling strategy
"""
# each epoch will be sampled over no_samples equally spaced intervals of lenght sample_delta
sample_delta = datetime.timedelta(days=7)
no_samples = 24
