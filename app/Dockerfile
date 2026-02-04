FROM python:3.13

WORKDIR /app
ARG directory=/this_is_fake_directory_in_prod_this_is_random

RUN apt-get update && apt-get install -y default-mysql-server default-mysql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir ${directory}
RUN useradd -M -d ${directory} ctf

COPY . .
COPY ./init.sql /tmp/init.sql
RUN mv flag.txt ${directory}/flag.txt
RUN chmod +x run.sh

RUN chown -R root:ctf ${directory} 
RUN chmod -R 750 ${directory}

EXPOSE 5000
CMD ["./run.sh"]