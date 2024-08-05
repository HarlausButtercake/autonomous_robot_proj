from datetime import datetime

def get_HMS():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    return formatted_time

def get_GMT7():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d_%H:%M:%S")
    return formatted_time
#     print(formatted_time)

if __name__ == "__main__":
    print(get_HMS())
