import os
import subprocess

def set_variable(key, value):
    # Need to escape double quotes if value has them, though our keys don't
    command = f'railway variable set "{key}={value}" --service PRISM'
    print(f"Setting {key}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to set {key}: {result.stderr}")
    else:
        print(f"Success for {key}")

# Railway injected database mappings
set_variable("POSTGRES_USER", "${{Postgres.PGUSER}}")
set_variable("POSTGRES_PASSWORD", "${{Postgres.PGPASSWORD}}")
set_variable("POSTGRES_DB", "${{Postgres.PGDATABASE}}")
set_variable("POSTGRES_HOST", "${{Postgres.PGHOST}}")
set_variable("POSTGRES_PORT", "${{Postgres.PGPORT}}")
set_variable("REDIS_URL", "${{Redis.REDIS_URL}}")

# Read from .env for the rest
with open('.env', 'r') as f:
    lines = f.readlines()

skip_keys = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_PORT", "REDIS_URL", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"]

for line in lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    
    parts = line.split('=', 1)
    if len(parts) == 2:
        key, value = parts[0].strip(), parts[1].strip()
        if key not in skip_keys:
            set_variable(key, value)

print("Finished setting variables!")
