# The runtime both libraries require
FROM python:3.13-slim

WORKDIR /app

# The solver and the client are installed from Test PyPI, with the public index available for their
# dependencies, exactly as the demo script documents
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/

COPY . .

# Unbuffered output, so the numbered demo sections appear in the container log as they are printed
ENV PYTHONUNBUFFERED=1

CMD ["python", "solver_visualizer_demo.py"]
