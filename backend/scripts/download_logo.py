import requests
import os

url = "https://lh3.googleusercontent.com/aida-public/AB6AXuCmo0MjyHYoX5jRhX7RDGVXen8paQIhImmLlh87xD7CQdJSaqS8305l7BPhZvugp2MUH7ikvjU_ZG1hg2d7Qk2thkNVTPVdwRZLwmbQjwfsNXzBGTXjSR-MpR8_Jb4er0nF1zBF3_XzTVnSb8bdKFW-0AFxf0ieIxRXybKjFsBK7cNbxn_m7YdoVYGpp4_tJfX1VQpvrrwCbNtt20ZIvEaKvuQHVk28Xzax3OU3YOpayJ2BHWIFZjwQD3M41npIm5BqoQ"
response = requests.get(url)
with open("data/logo.png", "wb") as f:
    f.write(response.content)
print("Logo downloaded!")
