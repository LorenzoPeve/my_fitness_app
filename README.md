## Installation
```
pip install --upgrade pip           # upgrade pip to at least 20.3
pip install "psycopg[binary,pool]"  # install binary dependencies
```

## Dev Database
Initialize Docker container
`docker run --name fitness-dev -d -p 5432:5432 -e POSTGRES_PASSWORD=mypass123 postgres`