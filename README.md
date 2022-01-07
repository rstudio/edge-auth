# edge-auth

This is a lambda@edge app with a terraform module for use via
cloudfront distribution to gate access to _whatever_ with some
basic auth warm fuzzies. All known user data is baked into the
lambda code at deployment time and there are no runtime
dependencies outside of the python standard library.

## Usage

The edge-auth lambda function should be configured as a
`lambda_function_association` in a given
`aws_cloudfront_distribution`, in either a `default_cache_behavior`
or `ordered_cache_behavior` block:

```hcl
module "secret_area_auth" {
  source = "github.com/rstudio/edge-auth"

  known_users = {
    jet   = "fuel"
    steel = "beams"
  }

  name_prefix = "secret-area"

  tags = {
    "com.example.serious/unit"    = "secrets"
    "com.example.serious/purpose" = "secrecy"
  }
}

resource "aws_cloudfront_distribution" "secret_area" {
  # ... many things ...

  default_cache_behavior {
    # ... many other things ...

    lambda_function_association {
      event_type   = "viewer-request"
      lambda_arn   = module.secret_area_auth.lambda_qualified_arn
      include_body = false
    }
  }

  # ... yet more things ...
}
```

In the above example, _every request_ through the
`default_cache_behavior` block will be gated at the
`"viewer-request"` event with a basic auth check. Only the
`known_users` will be allowed to complete the request.

## Behaviors

Successfully authenticated requests will be forwarded to the
cloudfront distribution target origin, which will then be
responsible for status, headers, etc.

Unsuccessful requests will result in one of the following, each of
which will include an `Edge-Auth-Error` response header with
human-readable details of what's wrong:

- no `known_users` configured :arrow_right: `500`
- no `Authorization` header in the request :arrow_right: `401`
- malformed `Authorization` header :arrow_right: `401`
- unknown user :arrow_right: `404` (:bulb: _this would "normally"
  be a `403`_ but this behavior is meant to be all sneaky nothing
to see here)
- any other unhandled errors :arrow_right: `500`
