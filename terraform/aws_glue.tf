# Base de datos Glue
resource "aws_glue_catalog_database" "raw_database" {
  name = "${var.project_name}_${var.environment}_raw_db"
}

# Crawler de Glue
resource "aws_glue_crawler" "raw_data_crawler" {
  database_name = aws_glue_catalog_database.raw_database.name
  name          = "${var.project_name}-${var.environment}-raw-crawler"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_bucket.bucket}/raw/"
  }

  schedule = "cron(0 */12 * * ? *)"  # Ejecuta cada 12 horas

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })

  depends_on = [
    aws_iam_role_policy_attachment.glue_service,
    aws_iam_role_policy.glue_s3_policy
  ]
}