FROM python:3.11 AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -t .

COPY . .

FROM python:3.11 AS runtime

WORKDIR /app

COPY --from=builder /build ./

CMD ["python", "-m", "cmd.main"]
