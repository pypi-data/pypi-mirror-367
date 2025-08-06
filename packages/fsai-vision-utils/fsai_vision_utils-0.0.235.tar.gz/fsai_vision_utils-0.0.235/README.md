# fsai-vision-utils

Vision utility functions and tools for batch processing and data management.

## Installation
```shell
poetry add fsai-vision-utils
```

## Tools

### AWS Batch Download Tool

Download multiple files from S3 using file IDs with multi-threading and retry logic.

#### Usage

```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file ids.txt \
    --aws_path s3://bucket/folder \
    --output_path ./images
```

#### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--ids_txt_file` | Yes | - | Text file with file IDs (one per line) |
| `--aws_path` | Yes | - | S3 base path (e.g., `s3://bucket/folder`) |
| `--output_path` | Yes | - | Local output directory |
| `--file_extension` | No | `jpg` | File extension to download |
| `--max_workers` | No | `50` | Number of concurrent downloads |
| `--max_retries` | No | `3` | Retry attempts per file |
| `--log_level` | No | `INFO` | Logging level |

#### Input Format

Create a text file with one file ID per line:
```
image_001
image_002
image_003
```

The tool downloads: `{aws_path}/{file_id}.{file_extension}`

#### Examples

**Basic download:**
```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file image_ids.txt \
    --aws_path s3://my-bucket/images \
    --output_path ./images
```

**Custom settings:**
```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file image_ids.txt \
    --aws_path s3://my-bucket/images \
    --output_path ./images \
    --file_extension png \
    --max_workers 100
```

#### Features

- Multi-threaded downloads (configurable workers)
- Automatic retry with exponential backoff
- Skips already downloaded files
- Progress tracking and statistics
- Graceful shutdown (Ctrl+C)
- Comprehensive logging

#### Requirements

- AWS CLI installed and configured
- Valid AWS credentials with S3 read access