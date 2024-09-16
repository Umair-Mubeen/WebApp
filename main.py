from fastapi import FastAPI
import logging

try:
    app = FastAPI()


    @app.get('/')
    async def index():
        message = 'Fast API Road Map'
        return f'{message}'

except Exception as e:
    logging.error(e, 'error')
    print(str(e))
