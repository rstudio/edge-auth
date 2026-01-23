# Python Upgrade Plan: 3.9 → 3.12 (Direct Path)

## Executive Summary

**Current State:** Python 3.9.10 (EOL: October 2025)
**Target Version:** Python 3.12.8 (Support until: October 2028)
**Timeline:** 2 weeks
**Risk Level:** LOW
**Deployment Strategy:** Production Blue/Green with Gradual Traffic Shift
**Environment:** Production only (no staging)

### Why Python 3.12?

- ✅ **Mature & Stable**: Released October 2023, production-ready
- ✅ **AWS Lambda Support**: Fully supported on Lambda@Edge
- ✅ **Performance**: 5-10% faster than Python 3.9
- ✅ **Long-term Support**: Security updates until October 2028
- ✅ **Better Error Messages**: Improved debugging experience
- ✅ **Type System Improvements**: Enhanced type hints and checking

### Why Skip 3.10 and 3.11?

- ✅ **Simple Codebase**: Only 2 Python files, ~100 LOC
- ✅ **No Dependencies**: Uses only Python standard library
- ✅ **Low Risk**: No breaking changes affecting our code
- ✅ **Faster Migration**: Reduces overall timeline by 1-2 weeks
- ✅ **Less Maintenance**: Fewer intermediate testing cycles

### No Staging Environment - Extra Precautions

⚠️ **IMPORTANT**: This plan deploys directly to production without a staging environment.

**Additional Risk Mitigation Measures:**
1. **Green Lambda Testing**: Deploy parallel Lambda for smoke testing
2. **Extended Monitoring**: 2-week intensive monitoring period
3. **Off-Hours Deployment**: Schedule during low-traffic window
4. **Quick Rollback Ready**: < 5 minute reversion capability
5. **Team On-Call**: Have team available during deployment window
6. **Gradual Validation**: Monitor extensively before declaring success

**Deployment Window Recommendations:**
- Choose lowest-traffic period (weeknight, early morning)
- Ensure team availability for 2-4 hours post-deployment
- Have rollback command ready to execute
- Monitor continuously for first 2 hours

---

## Current Environment Analysis

### Project Overview
- **Type**: AWS Lambda@Edge authentication handler
- **Runtime**: python3.9 (AWS Lambda)
- **Dependencies**:
  - Production: None (stdlib only)
  - Development: pytest, pytest-cov
- **Code Size**: 2 files (~100 LOC total)
- **Deployment**: Terraform-managed Lambda@Edge

### Files to Update
1. `.python-version`: 3.9.10 → 3.12.8
2. `.github/workflows/main.yml`: Update matrix to test 3.12.x
3. `main.tf`: runtime = "python3.9" → "python3.12"
4. `Pipfile.lock`: Update dev dependencies
5. `README.md`: Update version references (if any)

### Compatibility Assessment

**Python 3.9 → 3.12 Breaking Changes:**
- ✅ No impact on `base64` module usage
- ✅ No impact on `json` module usage
- ✅ No impact on `os` module usage
- ✅ Dict/set operations remain compatible
- ✅ Exception handling unchanged
- ✅ String operations compatible
- ⚠️ Minor: `warnings` module enhanced (backward compatible)

**Dependencies Compatibility:**
- ✅ pytest 7.1.3 → 7.4.0+ (supports Python 3.12)
- ✅ pytest-cov 3.0.0 → 4.1.0+ (supports Python 3.12)
- ✅ coverage 6.4.4 → 7.3.0+ (supports Python 3.12)

---

## Phase 1: Pre-Upgrade Preparation (Days 1-3)

### 1.1 Environment Setup

```bash
# Install Python 3.12
pyenv install 3.12.8

# Verify installation
pyenv versions
```

### 1.2 Create Feature Branch

```bash
# Already on: claude/python-upgrade-plan-uAg04
git status
```

### 1.3 Backup Current State

```bash
# Document current test results
make test > test_results_python39.txt

# Create rollback tag
git tag -a python-3.9-baseline -m "Python 3.9 baseline before upgrade"
```

### 1.4 Review Breaking Changes

- [ ] Review [Python 3.10 What's New](https://docs.python.org/3/whatsnew/3.10.html)
- [ ] Review [Python 3.11 What's New](https://docs.python.org/3/whatsnew/3.11.html)
- [ ] Review [Python 3.12 What's New](https://docs.python.org/3/whatsnew/3.12.html)
- [ ] Confirm no deprecated features used in edge_auth.py

---

## Phase 2: Development Environment Upgrade (Days 4-6)

### 2.1 Update Python Version File

```bash
# Update .python-version
echo "3.12.8" > .python-version
```

### 2.2 Update Pipenv Environment

```bash
# Remove old virtual environment
pipenv --rm

# Create new Python 3.12 environment
pipenv --python 3.12.8

# Install dependencies
make deps
```

### 2.3 Run Local Tests

```bash
# Run full test suite
make test

# Expected: All tests pass with 100% coverage
# Output should show:
# - test_edge_auth.py::test_handler[no_auth_401] PASSED
# - test_edge_auth.py::test_handler[invalid_auth_401] PASSED
# - test_edge_auth.py::test_handler[fake_403] PASSED
# - test_edge_auth.py::test_handler[ok] PASSED
# - Coverage: 100%
```

### 2.4 Check for Deprecation Warnings

```bash
# Run with all warnings enabled
pipenv run pytest -vv -W default --cov=edge_auth

# Scan code for deprecated patterns
python3.12 -m py_compile edge_auth.py
python3.12 -m py_compile test_edge_auth.py
```

### 2.5 Verify Code Quality

```bash
# Optional: Run static analysis if available
# python -m pylint edge_auth.py
# python -m mypy edge_auth.py

# Manual code review for:
# - Dict iteration patterns (still compatible)
# - Exception handling (no changes needed)
# - String formatting (compatible)
```

---

## Phase 3: CI/CD Configuration (Days 6-7)

### 3.1 Update GitHub Actions Workflow

Update `.github/workflows/main.yml`:

```yaml
name: main
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags: [v*]
jobs:
  main:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        # Test Python 3.12 alongside 3.9 during transition
        python-version: ['3.9.x', '3.12.x']
    steps:
      - uses: actions/checkout@v2
      - run: pipx install pipenv
      - uses: actions/setup-python@v2
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pipenv
      - run: make deps
      - run: make test
```

### 3.2 Commit and Push Changes

```bash
# Stage changes
git add .python-version Pipfile.lock .github/workflows/main.yml

# Commit
git commit -m "$(cat <<'EOF'
Update CI to test Python 3.9 and 3.12

- Add Python 3.12.x to CI test matrix
- Maintain Python 3.9.x for validation during transition
- Update Pipfile.lock with Python 3.12 compatible dependencies

Part of Python 3.9 → 3.12 upgrade plan.

https://claude.ai/code/session_01VF3C5uGNjLBYwz3tGH682E
EOF
)"

# Push to remote
git push -u origin claude/python-upgrade-plan-uAg04
```

### 3.3 Verify CI Pipeline

```bash
# Monitor GitHub Actions
gh run list --branch claude/python-upgrade-plan-uAg04
gh run watch

# Expected: Both Python 3.9.x and 3.12.x tests pass
```

---

## Phase 4: Blue/Green Production Preparation (Days 8-9)

### 4.1 Create Blue/Green Terraform Configuration

Since there's no staging environment, we'll create a parallel Lambda function for safe production testing.

**Update `main.tf` to support blue/green deployment:**

```hcl
# Add variable for runtime version
variable "python_runtime" {
  type        = string
  description = "Python runtime version"
  default     = "python3.9"
}

# Original Lambda (Blue - Python 3.9)
resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.zip.output_path
  function_name    = "${var.name_prefix}-edge-auth-lambda"
  handler          = "edge_auth.handler"
  publish          = true
  role             = aws_iam_role.lambda.arn
  runtime          = var.python_runtime
  source_code_hash = data.archive_file.zip.output_base64sha256

  lifecycle {
    create_before_destroy = true
  }

  tags = merge({ Name = "${var.name_prefix}-edge-auth-lambda" }, var.tags)
}

# New Lambda (Green - Python 3.12) - Temporary for testing
resource "aws_lambda_function" "lambda_green" {
  filename         = data.archive_file.zip.output_path
  function_name    = "${var.name_prefix}-edge-auth-lambda-green"
  handler          = "edge_auth.handler"
  publish          = true
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  source_code_hash = data.archive_file.zip.output_base64sha256

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    { Name = "${var.name_prefix}-edge-auth-lambda-green" },
    { DeploymentType = "blue-green-testing" },
    var.tags
  )
}

output "lambda_green_qualified_arn" {
  value       = aws_lambda_function.lambda_green.qualified_arn
  description = "Green Lambda ARN for blue/green deployment"
}
```

### 4.2 Deploy Green Lambda (Python 3.12)

```bash
# Review changes
terraform plan

# Expected: Creates new lambda_green resource

# Apply changes
terraform apply

# Verify both Lambdas exist
aws lambda list-functions --query 'Functions[?contains(FunctionName, `edge-auth`)].{Name:FunctionName,Runtime:Runtime}'
```

### 4.3 Manual Smoke Testing (Before Production Traffic)

**Test the Green Lambda directly (bypassing CloudFront):**

```bash
# Get the green Lambda ARN
GREEN_ARN=$(terraform output -raw lambda_green_qualified_arn)

# Create test event
cat > test_event_valid.json <<'EOF'
{
  "Records": [{
    "cf": {
      "request": {
        "headers": {
          "authorization": [{
            "key": "Authorization",
            "value": "Basic amV0OmZ1ZWw="
          }]
        }
      }
    }
  }]
}
EOF

# Test 1: Valid credentials (should return request object)
aws lambda invoke \
  --function-name ${GREEN_ARN} \
  --payload file://test_event_valid.json \
  response.json

cat response.json
# Expected: Request object returned (authentication passed)

# Test 2: Missing authorization
cat > test_event_noauth.json <<'EOF'
{
  "Records": [{
    "cf": {
      "request": {
        "headers": {}
      }
    }
  }]
}
EOF

aws lambda invoke \
  --function-name ${GREEN_ARN} \
  --payload file://test_event_noauth.json \
  response_noauth.json

cat response_noauth.json
# Expected: 401 status

# Test 3: Invalid authorization format
cat > test_event_invalid.json <<'EOF'
{
  "Records": [{
    "cf": {
      "request": {
        "headers": {
          "authorization": [{
            "key": "Authorization",
            "value": "Basic bmFyZgo="
          }]
        }
      }
    }
  }]
}
EOF

aws lambda invoke \
  --function-name ${GREEN_ARN} \
  --payload file://test_event_invalid.json \
  response_invalid.json

cat response_invalid.json
# Expected: 400 status

# Clean up test files
rm -f test_event_*.json response*.json
```

### 4.4 Verify Python 3.12 Specific Behavior

```bash
# Check CloudWatch logs for Python version
GREEN_FUNCTION_NAME=$(terraform output -raw lambda_green_qualified_arn | cut -d: -f7)

aws logs tail /aws/lambda/${GREEN_FUNCTION_NAME} --since 10m

# Look for:
# - No Python errors
# - Successful invocations
# - Normal execution patterns
```

### 4.5 Pre-Production Checklist

Before proceeding to production traffic shift:

- [ ] Green Lambda deployed successfully
- [ ] Manual smoke tests passed (all 4 test cases)
- [ ] CloudWatch logs show no Python errors
- [ ] Both Blue and Green Lambdas operational
- [ ] Rollback procedure documented and understood
- [ ] Monitoring dashboards ready
- [ ] Team notified of deployment window
- [ ] Off-hours deployment scheduled (if applicable)

---

## Phase 5: Production Deployment with Traffic Shift (Days 10-14)

### 5.1 Pre-Deployment Checklist

- [ ] Green Lambda tested successfully (Phase 4)
- [ ] Manual smoke tests passed
- [ ] CloudWatch logs show no errors
- [ ] Both Blue and Green Lambdas operational
- [ ] Rollback procedure ready
- [ ] Monitoring dashboards open
- [ ] Team notified of deployment window
- [ ] Deploy during low-traffic window if possible

### 5.2 Strategy: CloudFront Distribution Update

Since Lambda@Edge doesn't support weighted traffic splitting, we'll use a **time-based gradual rollout** where we switch the CloudFront distribution to point to the Green Lambda and monitor closely.

**Deployment Approach:**
1. **Hour 0**: Switch CloudFront to Green Lambda (Python 3.12)
2. **Hour 0-2**: Intensive monitoring (every 5-10 minutes)
3. **Hour 2-24**: Frequent monitoring (every 30-60 minutes)
4. **Day 2-7**: Daily monitoring
5. **Day 7+**: Normal monitoring, declare success

### 5.3 Switch CloudFront to Green Lambda

**Update CloudFront distribution to use Green Lambda:**

```bash
# Get the Green Lambda ARN
GREEN_ARN=$(terraform output -raw lambda_green_qualified_arn)

# Option 1: Update CloudFront via AWS Console
# - Go to CloudFront > Distributions
# - Select your distribution
# - Go to Behaviors > Edit
# - Update Lambda Function Association ARN to Green Lambda
# - Save and deploy

# Option 2: Update via Terraform (if CloudFront is managed in this repo)
# Update the aws_cloudfront_distribution resource
# Change lambda_arn from blue to green
# Run: terraform apply

# Option 3: Update via AWS CLI
DISTRIBUTION_ID="YOUR_DISTRIBUTION_ID"

# Get current config
aws cloudfront get-distribution-config \
  --id ${DISTRIBUTION_ID} \
  --query 'DistributionConfig' \
  > current_config.json

# Edit current_config.json manually to update Lambda ARN
# Then update distribution (requires ETag handling)
```

### 5.4 Alternative: Update Blue Lambda In-Place (Lower Risk)

**Recommended approach for single-distribution setups:**

Instead of switching CloudFront between Lambdas, update the Blue Lambda directly with create_before_destroy lifecycle:

```bash
# Update main.tf variable
terraform apply -var="python_runtime=python3.12"

# This will:
# 1. Create new Lambda version with Python 3.12
# 2. Update CloudFront association
# 3. Delete old Lambda version

# Rollback if needed:
terraform apply -var="python_runtime=python3.9"
```

### 5.5 Monitor Production (Critical - No Staging Safety Net)

```bash
# Real-time log monitoring
aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --filter-pattern "ERROR"

# CloudWatch metrics dashboard
# - Lambda Errors
# - Lambda Duration (P50, P95, P99)
# - Lambda Invocations
# - CloudFront 4xx/5xx rates
```

**Automated Alerting:**
- Error rate threshold: > 0.5%
- Latency threshold: P95 > 150% of baseline
- Invocation errors: Any increase

### 5.6 Monitoring Schedule (Extra Vigilance Required)

Since we're deploying directly to production without staging validation:

**Hour 0-1: CRITICAL WINDOW**
- Monitor CloudWatch Logs in real-time (keep terminal open)
- Check metrics every 5 minutes
- Have rollback command ready to execute
- Watch for: ANY errors, increased latency, authentication failures

**Hour 1-4: HIGH ALERT**
- Monitor every 15 minutes
- Review CloudWatch dashboard
- Check error rates and latency
- Validate sample requests manually

**Hour 4-24: ACTIVE MONITORING**
- Monitor every 30-60 minutes
- Review aggregated metrics
- Compare with baseline (same time yesterday)
- Spot-check authentication flows

**Day 2-7: ELEVATED MONITORING**
- Monitor 3-4 times daily
- Daily metric review
- Compare week-over-week trends
- Gather feedback from users (if applicable)

**Day 7-14: NORMAL MONITORING**
- Daily check-ins
- Weekly comprehensive review
- Document any anomalies
- Prepare success report

### 5.7 Declare Success

**Success Criteria:**
- ✅ 7 days in production without issues
- ✅ Error rate < baseline
- ✅ Latency within 10% of baseline
- ✅ Zero authentication failures for valid users
- ✅ No Python-related errors in logs

```bash
# Document success metrics
echo "Python 3.12 Migration - Production Metrics" > migration_success.txt
echo "Deployment Date: $(date)" >> migration_success.txt
echo "Days in Production: 7" >> migration_success.txt
# Add CloudWatch metric screenshots
```

---

## Phase 6: Cleanup & Documentation (Days 15-16)

### 6.1 Remove Python 3.9 from CI

Update `.github/workflows/main.yml`:

```yaml
strategy:
  matrix:
    # Only test Python 3.12 now
    python-version: ['3.12.x']
```

### 6.2 Update Documentation

```bash
# Update README if it mentions Python version
# Update deployment docs
# Update developer setup guides
```

### 6.3 Clean Up Terraform Resources

```bash
# Remove the green Lambda (temporary testing resource)
# Update main.tf to remove lambda_green resource

# Option 1: Remove green Lambda via Terraform
# Comment out or delete lambda_green resource in main.tf
terraform apply

# Option 2: Keep green Lambda for future testing
# Tag it as "testing" and document its purpose
```

### 6.4 Communicate Success

```markdown
## Python 3.12 Upgrade - Complete ✅

**Summary:**
- Upgraded from Python 3.9.10 to Python 3.12.8
- Zero downtime deployment
- No production issues
- Performance: [X% improvement/similar]

**Timeline:**
- Planning: [dates]
- Staging: [dates]
- Production: [dates]

**Lessons Learned:**
- [Add any insights]

**Next Steps:**
- Monitor for 30 days
- Consider upgrading to Python 3.13 in 2026
```

---

## Rollback Plan

### Immediate Rollback (< 5 minutes)

**Scenario 1: During Development/Testing**
```bash
# Revert local changes
git revert HEAD
echo "3.9.10" > .python-version
pipenv --python 3.9
```

**Scenario 2: During Production (CRITICAL)**
```bash
# Update Lambda to Python 3.9
terraform apply -var="python_runtime=python3.9"

# Or: Point CloudFront to old Lambda version
# Update lambda_function_association in CloudFront distribution
```

### Rollback Triggers

**Automatic Rollback If:**
- Error rate > 1% for 5 minutes
- Lambda errors > 10 in 5 minutes
- P95 latency > 200% of baseline
- Any authentication failures for known valid users

**Manual Rollback If:**
- Unexpected Python errors in logs
- Customer reports of authentication issues
- Memory or performance degradation
- Team decision to rollback

### Rollback Testing

**IMPORTANT:** Without a staging environment, rollback practice is critical.

```bash
# Test rollback procedure with Green Lambda BEFORE production deployment
# Day 9: Practice rollback with local environment

# 1. Verify current state
terraform state list | grep lambda

# 2. Practice rollback command (don't execute in prod)
# Dry-run only:
terraform plan -var="python_runtime=python3.9"

# 3. Prepare rollback script
cat > rollback.sh <<'EOF'
#!/bin/bash
set -e
echo "EMERGENCY ROLLBACK: Reverting to Python 3.9"
terraform apply -auto-approve -var="python_runtime=python3.9"
aws logs tail /aws/lambda/${FUNCTION_NAME} --since 5m
EOF

chmod +x rollback.sh

# 4. Document the exact command
echo "terraform apply -auto-approve -var='python_runtime=python3.9'" > ROLLBACK_COMMAND.txt

# 5. Have this command ready to copy-paste during deployment
```

**Rollback Drill Checklist:**
- [ ] Know exact rollback command
- [ ] Have terminal ready with command
- [ ] Know how to monitor CloudWatch
- [ ] Know expected metrics/baselines
- [ ] Have team communication channel open
- [ ] Document decision criteria for rollback

---

## Testing Strategy

### Unit Tests
```bash
# Run full test suite
make test

# Tests to verify:
✅ test_handler[no_auth_401] - Missing auth header → 401
✅ test_handler[invalid_auth_401] - Invalid auth format → 400
✅ test_handler[fake_403] - Unknown user → 404
✅ test_handler[ok] - Valid credentials → Request forwarded

# Coverage requirement: 100%
```

### Integration Tests (Staging)
```bash
# Create integration test script
cat > test_integration.sh <<'EOF'
#!/bin/bash
set -e

BASE_URL="${1:-https://staging.example.com}"

echo "Testing Missing Authorization..."
curl -sf -o /dev/null -w "%{http_code}" "$BASE_URL/test" | grep -q 401

echo "Testing Invalid Authorization..."
curl -sf -o /dev/null -w "%{http_code}" -H "Authorization: Basic invalid" "$BASE_URL/test" | grep -q 400

echo "Testing Unknown User..."
curl -sf -o /dev/null -w "%{http_code}" -u "fake:user" "$BASE_URL/test" | grep -q 404

echo "Testing Valid User..."
curl -sf -o /dev/null -w "%{http_code}" -u "$VALID_USER:$VALID_TOKEN" "$BASE_URL/test" | grep -q 200

echo "✅ All integration tests passed!"
EOF

chmod +x test_integration.sh
./test_integration.sh
```

### Performance Tests
```bash
# Simple load test with Apache Bench
ab -n 1000 -c 10 -A jet:fuel https://staging.example.com/test

# Expected metrics:
# - Mean time per request: < 100ms
# - 99th percentile: < 200ms
# - Failed requests: 0
```

### Security Validation
```bash
# Verify authentication still works
# Verify error messages don't leak sensitive info
# Verify CloudWatch logs don't contain tokens

# Test various attack vectors:
# - SQL injection in credentials (should fail gracefully)
# - Long credential strings (should handle)
# - Special characters in credentials (should work if valid)
```

---

## Timeline Summary

| Phase | Duration | Activities | Risk | Rollback |
|-------|----------|------------|------|----------|
| **1. Preparation** | Days 1-3 | Environment setup, backups, testing plan | None | N/A |
| **2. Development** | Days 4-6 | Local testing, code validation | Low | Instant |
| **3. CI/CD** | Days 6-7 | GitHub Actions, automated tests | Low | Instant |
| **4. Blue/Green Prep** | Days 8-9 | Green Lambda deploy, smoke tests | Low | N/A |
| **5. Production Deploy** | Days 10-14 | Traffic shift, intensive monitoring | **Medium-High** | < 5 min |
| **6. Cleanup** | Days 15-16 | Remove green Lambda, documentation | Low | N/A |
| **Total** | **2-2.5 weeks** | **Full migration (no staging)** | **Medium** | **< 5 min** |

**Note:** Production deployment risk is higher without staging environment. Compensate with:
- Extended monitoring periods
- Off-hours deployment window
- Quick rollback capability (< 5 minutes)
- Team on-call during critical window

---

## Risk Assessment

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking API changes | Low | High | Comprehensive testing, staging validation |
| Lambda cold start increase | Low | Low | Monitor performance metrics |
| Dependency incompatibility | Low | Medium | Pre-validate pytest/pytest-cov compatibility |
| Production authentication failure | Very Low | Critical | Blue/green deployment, instant rollback |
| CloudWatch logging issues | Very Low | Low | Verify logs in staging first |
| Terraform deployment failure | Low | Medium | Test in staging, have rollback ready |

### Overall Risk: **LOW**

**Why Low Risk:**
- ✅ No production dependencies (stdlib only)
- ✅ Simple codebase (2 files, ~100 LOC)
- ✅ Comprehensive test coverage (100%)
- ✅ Proven Python 3.12 stability
- ✅ AWS Lambda official support
- ✅ Phased deployment approach
- ✅ Quick rollback capability
- ✅ No breaking changes in stdlib APIs used

---

## Success Metrics

### Technical Metrics
- ✅ All unit tests pass on Python 3.12
- ✅ 100% test coverage maintained
- ✅ Zero production errors related to Python version
- ✅ Performance within 10% of baseline (or better)
- ✅ Successful 7-day production soak test

### Business Metrics
- ✅ Zero downtime during migration
- ✅ No customer-reported authentication issues
- ✅ Security support extended to 2028
- ✅ Team confidence in new setup

### Operational Metrics
- ✅ CI/CD pipeline passing on Python 3.12
- ✅ Documentation updated
- ✅ Team trained on new environment
- ✅ Rollback procedure tested and documented

---

## Quick Reference Commands

### Development
```bash
# Switch to Python 3.12
echo "3.12.8" > .python-version
pipenv --python 3.12.8
make deps
make test
```

### Deployment
```bash
# Deploy to staging
terraform plan
terraform apply

# Monitor logs
aws logs tail /aws/lambda/$(terraform output -raw lambda_arn | cut -d: -f7) --follow
```

### Rollback
```bash
# Emergency rollback
echo "3.9.10" > .python-version
git checkout main.tf
terraform apply
```

### Monitoring
```bash
# Check GitHub Actions
gh run list --limit 5

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=${FUNCTION_NAME} \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

---

## Appendix A: Python 3.9 → 3.12 Key Changes

### Performance Improvements
- **PEP 709**: Comprehension inlining (5-11% faster list/dict/set comprehensions)
- **Improved asyncio**: Faster async/await operations
- **Faster attribute access**: 10-15% improvement
- **Optimized imports**: Reduced startup time

### New Features (Optional to Adopt)
- **PEP 695**: Type parameter syntax (`def func[T](x: T) -> T`)
- **PEP 701**: f-string improvements
- **PEP 688**: Better buffer protocol
- **Improved error messages**: More helpful tracebacks

### Removals (None Affecting This Project)
- Deprecated modules removed: none used in edge_auth.py
- Deprecated APIs removed: none used in edge_auth.py

---

## Appendix B: Dependency Version Matrix

| Package | Python 3.9 | Python 3.12 | Notes |
|---------|------------|-------------|-------|
| pytest | 7.1.3 | 7.4.0+ | Fully compatible |
| pytest-cov | 3.0.0 | 4.1.0+ | Fully compatible |
| coverage | 6.4.4 | 7.3.0+ | Fully compatible |
| attrs | 22.1.0 | 23.1.0+ | Fully compatible |
| pluggy | 1.0.0 | 1.3.0+ | Fully compatible |

**Action**: Run `pipenv update --dev` to get latest compatible versions

---

## Appendix C: AWS Lambda Python 3.12 Support

### Lambda Runtime Information
- **Runtime ID**: `python3.12`
- **Python Version**: 3.12.x
- **Architecture**: x86_64, arm64
- **Release Date**: November 2023
- **Status**: Generally Available (GA)

### Lambda@Edge Support
- ✅ Python 3.12 supported on Lambda@Edge
- ✅ No additional configuration required
- ✅ Same deployment process as Python 3.9

### AWS SDK Compatibility
- Not applicable (no boto3/AWS SDK used in this project)

---

## Contact & Support

**Questions?**
- Review this plan in: `/home/user/edge-auth/PYTHON_UPGRADE_PLAN.md`
- GitHub branch: `claude/python-upgrade-plan-uAg04`
- Session: https://claude.ai/code/session_01VF3C5uGNjLBYwz3tGH682E

**Rollback Support:**
- Immediate: Revert terraform changes
- Emergency: Contact DevOps team
- Escalation: [Add team contact info]

---

**Plan Version:** 2.0 (Direct 3.9 → 3.12 Path)
**Last Updated:** 2026-01-23
**Status:** Ready for Implementation
