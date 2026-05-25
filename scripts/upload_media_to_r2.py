"""
One-off: upload local media/ files to Cloudflare R2 so existing artwork
image paths resolve after the Fly migration.

Usage:
    # Load the same R2_* env vars used by the app, then:
    python scripts/upload_media_to_r2.py            # upload everything missing
    python scripts/upload_media_to_r2.py --dry-run  # show what would upload
    python scripts/upload_media_to_r2.py --force    # re-upload even if present

Requires: boto3 (already in requirements.txt).
"""
import argparse
import mimetypes
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / 'media'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true', help='re-upload files even if already present')
    args = parser.parse_args()

    load_dotenv(BASE_DIR / '.env')

    bucket = os.environ['R2_BUCKET_NAME']
    client = boto3.client(
        's3',
        endpoint_url=os.environ['R2_ENDPOINT_URL'],
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        region_name='auto',
    )

    if not MEDIA_DIR.is_dir():
        sys.exit(f'No media directory found at {MEDIA_DIR}')

    files = [p for p in MEDIA_DIR.rglob('*') if p.is_file()]
    if not files:
        print('No files to upload.')
        return

    uploaded = skipped = 0
    for path in files:
        key = str(path.relative_to(MEDIA_DIR)).replace(os.sep, '/')

        if not args.force and object_exists(client, bucket, key):
            print(f'skip  {key}')
            skipped += 1
            continue

        content_type = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'

        if args.dry_run:
            print(f'would upload  {key}  ({content_type})')
        else:
            client.upload_file(
                str(path), bucket, key,
                ExtraArgs={'ContentType': content_type},
            )
            print(f'uploaded  {key}')
        uploaded += 1

    print(f'\nDone. {uploaded} uploaded, {skipped} skipped.')


def object_exists(client, bucket, key):
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] in ('404', 'NoSuchKey', 'NotFound'):
            return False
        raise


if __name__ == '__main__':
    main()
