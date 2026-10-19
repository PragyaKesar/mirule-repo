# miRULE: PHP front end on Apache, Python back end.
# Serves the webserver on port 7860.
# Python 3.13 matches the version used to train the saved models.
FROM python:3.13-slim-trixie

RUN apt-get update \
 && apt-get install -y --no-install-recommends apache2 libapache2-mod-php \
 && rm -rf /var/lib/apt/lists/* /var/www/html/index.html

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY mirule /app/mirule
COPY models /app/models
COPY web/ /var/www/html/

# Apache listens on 7860, logs to the console and runs as a non-root user.
RUN sed -i 's/^Listen 80$/Listen 7860/' /etc/apache2/ports.conf \
 && sed -i 's/<VirtualHost \*:80>/<VirtualHost *:7860>/' /etc/apache2/sites-available/000-default.conf \
 && sed -i 's#ErrorLog .*#ErrorLog /dev/stderr#; s#CustomLog .*#CustomLog /dev/stdout combined#' /etc/apache2/sites-available/000-default.conf \
 && echo 'ServerName localhost' >> /etc/apache2/apache2.conf \
 && echo 'DirectoryIndex index.php' >> /etc/apache2/apache2.conf \
 && mkdir -p /var/run/apache2 /var/lock/apache2 /var/log/apache2 \
 && chown -R 1000:1000 /var/run/apache2 /var/lock/apache2 /var/log/apache2

ENV MIRULE_PYTHON=/usr/local/bin/python \
    MIRULE_ROOT=/app

USER 1000
EXPOSE 7860
CMD ["apache2ctl", "-D", "FOREGROUND"]
