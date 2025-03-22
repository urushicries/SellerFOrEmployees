import hashlib

# Set your password
password = "AWcoolPassword"

# Hash the password using SHA-256
password_hash = hashlib.sha256(password.encode()).hexdigest()

# Print the hashed password
print("Hashed password:", password_hash)
