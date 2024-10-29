# Outputs
output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "glue_database_name" {
  value = aws_glue_catalog_database.raw_database.name
}

output "glue_crawler_name" {
  value = aws_glue_crawler.raw_data_crawler.name
}