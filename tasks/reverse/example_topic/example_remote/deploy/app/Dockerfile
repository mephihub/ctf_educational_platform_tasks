FROM gcc:latest

COPY main.c /
RUN apt-get install -y socat
RUN gcc -o app main.c

ENTRYPOINT [ "socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/app" ]