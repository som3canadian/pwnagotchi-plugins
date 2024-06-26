# pwnagotchi-plugins

## S3_bucket

`/etc/pwnagotchi/config.toml`

```toml
main.plugins.s3_bucket.enabled = true
main.plugins.s3_bucket.access_key = "access_key_string"
main.plugins.s3_bucket.secret_key = "secret_key_string"
main.plugins.s3_bucket.bucket_name = "pwnagotchi"
main.plugins.s3_bucket.src_folder = "/home/pi/handshakes"
main.plugins.s3_bucket.is_cloudflare = true
main.plugins.s3_bucket.cf_account = "cf_account_string"
main.plugins.s3_bucket.interval = 1
main.plugins.s3_bucket.max_tries = 5
```
