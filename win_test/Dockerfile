FROM ubuntu:22.04
RUN apt update && apt install -y wine64 xvfb
ENV WINEARCH=win64
ENV DISPLAY=:0
CMD ["bash"]
