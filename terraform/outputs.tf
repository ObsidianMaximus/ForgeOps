output "visitor_api_url" {
  description = "Public endpoint for the visitor count API"
  value       = aws_apigatewayv2_api.visitor_api.api_endpoint
}