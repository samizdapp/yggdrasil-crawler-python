FROM python

COPY yggdrasil-crawler . 

CMD ["python", "crawlerctl.py"]