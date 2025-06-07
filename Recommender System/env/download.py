import gdown

url = "https://drive.google.com/uc?id=1ShHBcpa3tAzAFFRfM2iL4wp_dr24T6_e"
# output = "../init.sql"  # Adjust path if needed
gdown.download(url, quiet=False)
