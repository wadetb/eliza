import random
import string

max_length = 255

# Generate a random string of lowercase letters and digits
random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=max_length))

print(random_string)