variable "known_users" {
  type = map(string)
}

variable "name_prefix" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {
    "github-repo" = "github.com/rstudio/edge-auth"
  }
}

data "archive_file" "zip" {
  type        = "zip"
  output_path = "${var.name_prefix}-edge_auth.zip"

  source {
    content  = <<-EDGEAUTHPY
      ${file("${path.module}/edge_auth.py")}

      KNOWN_USERS_JSON = """
      ${jsonencode(var.known_users)}
      """
    EDGEAUTHPY
    filename = "edge_auth.py"
  }
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = [
        "edgelambda.amazonaws.com",
        "lambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name_prefix}-edge-auth-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge({ Name = "${var.name_prefix}-edge-auth-lambda-role" }, var.tags)
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.zip.output_path
  function_name    = "${var.name_prefix}-edge-auth-lambda"
  handler          = "edge_auth.handler"
  publish          = true
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256

  lifecycle {
    create_before_destroy = true
  }

  tags = merge({ Name = "${var.name_prefix}-edge-auth-lambda" }, var.tags)
}

output "lambda_arn" {
  value = aws_lambda_function.lambda.arn
}

output "lambda_qualified_arn" {
  value = aws_lambda_function.lambda.qualified_arn
}
