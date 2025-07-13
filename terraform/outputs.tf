# terraform/outputs.tf

output "ecr_repository_url" {
  description = "URL of the created ECR repository"
  value       = aws_ecr_repository.fluxpilot.repository_url
}

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution IAM role"
  value       = aws_iam_role.sagemaker_execution.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for SageMaker endpoint"
  value       = aws_cloudwatch_log_group.sagemaker_logs.name
}
