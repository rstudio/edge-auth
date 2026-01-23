# Python Upgrade Plan: 3.9 → 3.12 (Direct Path)

## Executive Summary

**Current State:** Python 3.9.10 (EOL: October 2025)
**Target Version:** Python 3.12.8 (Support until: October 2028)
**Timeline:** 2-3 weeks
**Risk Level:** LOW
**Deployment Strategy:** Blue/Green with Canary Release

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

## Phase 1: Pre-Upgrade Preparation (Days 1-2)

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

## Phase 2: Development Environment Upgrade (Days 3-5)

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

## Phase 3: CI/CD Configuration (Days 5-6)

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

## Phase 4: Staging Deployment (Days 7-10)

### 4.1 Update Terraform Configuration

**Option A: Create Staging-Specific Variable**

```hcl
# Add to main.tf or create staging.tfvars
variable "python_runtime" {
  type    = string
  default = "python3.12"
}

resource "aws_lambda_function" "lambda" {
  # ... existing config ...
  runtime = var.python_runtime
  # ... rest of config ...
}
```

**Option B: Direct Update (Recommended for this project)**

Update `main.tf` line 59:
```hcl
runtime = "python3.12"
```

### 4.2 Deploy to Staging Environment

```bash
# Review changes
terraform plan

# Expected output:
# ~ aws_lambda_function.lambda
#   ~ runtime: "python3.9" -> "python3.12"

# Apply changes to staging
terraform apply -target=aws_lambda_function.lambda

# Note: This will create a new Lambda version
```

### 4.3 Staging Validation Tests

**Test 1: Valid Authentication**
```bash
# Test with valid credentials
curl -v -u "jet:fuel" https://staging.example.com/protected/resource

# Expected: 200 OK (or resource response)
```

**Test 2: Missing Authorization**
```bash
# Test without credentials
curl -v https://staging.example.com/protected/resource

# Expected: 401 with WWW-Authenticate header
```

**Test 3: Invalid Authorization Format**
```bash
# Test with malformed auth
curl -v -H "Authorization: Basic bmFyZgo=" https://staging.example.com/protected/resource

# Expected: 400 with Edge-Auth-Error header
```

**Test 4: Unknown User**
```bash
# Test with invalid credentials
curl -v -u "fake:user" https://staging.example.com/protected/resource

# Expected: 404 with Edge-Auth-Error header
```

### 4.4 Monitor CloudWatch Logs

```bash
# Get Lambda function name
FUNCTION_NAME=$(terraform output -raw lambda_arn | cut -d: -f7)

# Tail logs
aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --since 1h

# Look for:
# - No Python errors
# - Successful invocations
# - Normal response times
```

### 4.5 Performance Comparison

```bash
# Monitor Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=${FUNCTION_NAME} \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Compare with Python 3.9 baseline
# Expected: Similar or better performance
```

### 4.6 Soak Test

- **Duration**: 48-72 hours
- **Monitor**: Error rates, latency, invocation count
- **Success Criteria**:
  - Zero authentication errors for valid users
  - Error rate < 0.1%
  - P95 latency within 10% of baseline

---

## Phase 5: Production Deployment (Days 11-15)

### 5.1 Pre-Deployment Checklist

- [ ] All staging tests passed
- [ ] 48-hour soak test completed successfully
- [ ] CloudWatch logs show no errors
- [ ] Performance metrics acceptable
- [ ] Rollback procedure tested and documented
- [ ] Team notified of deployment window

### 5.2 Blue/Green Deployment Setup

**Create Production Blue/Green Lambda**

```hcl
# Temporarily create second Lambda for canary
resource "aws_lambda_function" "lambda_python312" {
  filename         = data.archive_file.zip.output_path
  function_name    = "${var.name_prefix}-edge-auth-lambda-py312"
  handler          = "edge_auth.handler"
  publish          = true
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"  # New version
  source_code_hash = data.archive_file.zip.output_base64sha256

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    { Name = "${var.name_prefix}-edge-auth-lambda-py312" },
    { Purpose = "python312-canary" },
    var.tags
  )
}

output "lambda_python312_qualified_arn" {
  value = aws_lambda_function.lambda_python312.qualified_arn
}
```

### 5.3 Canary Deployment - 10% Traffic

**Option 1: Using CloudFront Function Association Weighted**
*(Note: Lambda@Edge doesn't support native traffic splitting, use CloudFront distribution cloning or DNS-based approach)*

**Option 2: Time-Based Gradual Rollout (Recommended)**

```bash
# Day 1: Deploy during low-traffic window
# Update production Lambda to Python 3.12
terraform apply

# Monitor for 2 hours
# If issues: terraform apply -var="python_runtime=3.9" (rollback)
```

**Option 3: Create Separate CloudFront Distribution for Canary**

```hcl
# Clone CloudFront distribution with Python 3.12 Lambda
# Route 10% of DNS traffic via weighted routing
```

### 5.4 Monitor Production (Critical)

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

### 5.5 Progressive Rollout

**Hour 0-2: Initial Deployment**
- Deploy Python 3.12 Lambda
- Monitor every 15 minutes
- Quick rollback if errors detected

**Hour 2-24: First Day Monitoring**
- Monitor every hour
- Check CloudWatch dashboards
- Review error logs
- Validate authentication success rate

**Day 2-7: Extended Monitoring**
- Daily monitoring
- Weekly metric review
- Compare against Python 3.9 baseline

### 5.6 Declare Success

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

## Phase 6: Cleanup & Documentation (Days 16-17)

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
# Remove any blue/green temporary resources
# Simplify terraform config back to single Lambda
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

**Scenario 1: During Staging**
```bash
# Revert Terraform changes
git revert HEAD
terraform apply
```

**Scenario 2: During Production**
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

```bash
# Test rollback procedure in staging BEFORE production deployment
# Day 9: Practice rollback

# 1. Deploy Python 3.12 to staging
terraform apply

# 2. Perform rollback
terraform apply -var="python_runtime=python3.9"

# 3. Verify functionality restored
make test
# Run integration tests

# 4. Re-deploy Python 3.12
terraform apply -var="python_runtime=python3.12"
```

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
| **1. Preparation** | Days 1-2 | Environment setup, backups | None | N/A |
| **2. Development** | Days 3-5 | Local testing, code validation | Low | Instant |
| **3. CI/CD** | Days 5-6 | GitHub Actions, automated tests | Low | Instant |
| **4. Staging** | Days 7-10 | Deploy & validate, soak test | Medium | 5 min |
| **5. Production** | Days 11-15 | Gradual rollout, monitoring | Medium | 5 min |
| **6. Cleanup** | Days 16-17 | Documentation, communication | Low | N/A |
| **Total** | **2-3 weeks** | **Full migration** | **Low** | **< 5 min** |

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
