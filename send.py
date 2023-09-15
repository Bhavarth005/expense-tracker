import requests
import random

def send():
    email = "vbhavarth123@gmail.com"
    otp = random.randint(111111,999999)
    request = ("http://localhost:8081/?email="+email+"&otp="+ str(otp))
    response = requests.get(request)
    # print("Response Content:")
    # print(response)

    # Close the connection

if __name__ == '__main__':
    send()