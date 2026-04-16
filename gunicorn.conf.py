import os

# Bind to the PORT env var provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker configuration
workers = 2
threads = 2
timeout = 120
