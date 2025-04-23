import os
import subprocess
def load_env_from_system():
    try:
        # Read from /etc/environment
        with open('/etc/environment', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Strip quotes if present
                    value = value.strip('\'"')
                    os.environ[key] = value
        return True
    except Exception as e:
        print(f"Failed to load environment variables: {e}")
        return
    