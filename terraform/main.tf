# terraform/main.tf

resource "aws_ecr_repository" "fluxpilot" {
  name                 = "fluxpilot"
  image_tag_mutability = "MUTABLE"
}

resource "aws_iam_role" "sagemaker_execution" {
  name = "fluxpilot-sagemaker-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "sagemaker.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy_attachment" "attach_sagemaker" {
  name       = "fluxpilot-sagemaker-policy-attach"
  roles      = [aws_iam_role.sagemaker_execution.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_cloudwatch_log_group" "sagemaker_logs" {
  name              = "/aws/sagemaker/Endpoints/fluxpilot-endpoint"
  retention_in_days = 14
}
