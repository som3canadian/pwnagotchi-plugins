import logging
import boto3
import os
import io
import threading
import pwnagotchi.plugins as plugins
# from pwnagotchi.utils import StatusFile

# pip3 install boto3

# Build with R2 bucket (CloudFlare) in mind but should work with others S3 compatible services

class S3Bucket(plugins.Plugin):
  __author__ = 'som3canadian'
  __version__ = '1.0.0'
  __license__ = 'GLWTS'
  __description__ = 'Uploads the handshake file to an S3 compatible bucket'

  def __init__(self):
    self.ready = False
    self.tries = 0
    self.lock = threading.Lock()
    self.internet_connected = "False"
    # self.status = StatusFile('/root/.s3_bucket.status')

  def on_loaded(self):
    logging.info("[S3Bucket] plugin loaded")
    # check if access_key and secret_key are set
    if not self.options['access_key']:
      logging.error("access_key is not set")
      self.ready = False
    if not self.options['secret_key']:
      logging.error("secret_key is not set")
      self.ready = False

    # check if bucket_name is set
    if not self.options['bucket_name']:
      logging.error("bucket_name is not set")
      self.ready = False

    # is is_cloudflare = True, then check for cf_account is set
    if self.options['is_cloudflare'] and not self.options['cf_account']:
      logging.error("cf_account is not set")
      self.ready = False

    # check if src_folder is set
    if not self.options['src_folder']:
      logging.error("src_folder is not set")
      self.ready = False

    self.ready = True
    logging.info("[S3Bucket] All config options found.")

  def on_internet_available(self, agent):
      if self.lock.locked():
            return
      self.internet_connected = "True"
      self.s3_upload_folder(agent)

  def on_handshake(self, agent, filename, access_point, client_station):
    self.s3_upload_folder(agent)

  def s3_handshake_upload(self, agent, filename):
    if self.internet_connected == "False":
      return
    if self.lock.locked():
      return
    if self.options['max_tries'] and self.tries >= self.options['max_tries']:
      logging.error("[S3_Bucket] max_tries reached")
    with self.lock:
      try:
          logging.info("detected a new handshake and internet connectivity!")
          # file name without extension
          temp_filename = os.path.splitext(filename)[0]
          file_path = self.options['src_folder'] + "/" + temp_filename

          self.s3 = boto3.client(
            service_name='s3',
            endpoint_url="https://" + self.options['cf_account'] + ".r2.cloudflarestorage.com",
            aws_access_key_id=self.options['access_key'],
            aws_secret_access_key=self.options['secret_key'],
            region_name='auto'
          )
          with open(file_path + ".22000", "rb") as f:
            self.s3.upload_fileobj(f, self.options['bucket_name'], filename + ".22000")
            logging.info("[S3_Bucket] uploaded handshake(.22000) file: " + filename)
          with open(file_path + ".pcap", "rb") as f:
            self.s3.upload_fileobj(f, self.options['bucket_name'], filename + ".pcap")
            logging.info("[S3_Bucket] uploaded handshake(.pcap) file: " + filename)

      except Exception as e:
        logging.error("[S3_Bucket] error uploading file: " + str(e))
        self.tries += 1

  def s3_upload_folder(self, agent):
    if self.internet_connected == "False":
      return
    if self.status.newer_then_days(self.options['interval']):
      logging.info("[S3_Bucket] interval not reached")
      return
    if self.lock.locked():
      return
    if self.options['max_tries'] and self.tries >= self.options['max_tries']:
      logging.error("max_tries reached")
      return
    with self.lock:
      try:
          logging.info("[S3_Bucket] detected a new session and internet connectivity!")

          self.s3 = boto3.client(
            service_name='s3',
            endpoint_url="https://" + self.options['cf_account'] + ".r2.cloudflarestorage.com",
            aws_access_key_id=self.options['access_key'],
            aws_secret_access_key=self.options['secret_key'],
            region_name='auto'
          )
          # for every file in src_folder Upload/Update the file (.pcap or .22000 file)
          for file in os.listdir(self.options['src_folder']):
            if file.endswith(".pcap") or file.endswith(".22000"):
              with open(self.options['src_folder'] + "/" + file, "rb") as f:
                self.s3.upload_fileobj(f, self.options['bucket_name'], file)
                logging.info("[S3_Bucket] uploaded file: " + file)

      except Exception as e:
        logging.error("[S3_Bucket] error uploading file: " + str(e))
        self.tries += 1