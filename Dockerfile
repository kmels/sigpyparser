FROM python:3.7.5-slim
COPY . /src
RUN cd src && pip3 install -r requirements.txt --user
RUN cd src && python3 setup.py install --user 
CMD ["python3","/src/signal_parser/zmq_rep.py"]
