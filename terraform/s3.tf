# Bucket S3
resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.project_name}-${var.environment}-raw-data"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Configuración de versioning para S3
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

