# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please send an email with the details to the project maintainers by creating a **private security advisory** on GitHub:

1. Go to the repository's Security tab
2. Click "Report a vulnerability"
3. Fill in the details

Alternatively, open a GitHub issue with the title "SECURITY: [Brief Description]" and we will contact you privately.

### What to Include

When reporting a vulnerability, please include:

- Type of vulnerability (e.g., API key exposure, SQL injection, authentication bypass)
- Step-by-step instructions to reproduce the issue
- Potential impact of the vulnerability
- Suggested fix (if you have one)
- Your contact information for follow-up

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Status Update**: Every 7 days until resolved
- **Fix Release**: Depends on severity (critical issues within 7 days)

## Security Best Practices

### For Users

**API Keys:**
- Never commit `.env` file to version control
- Use environment variables for all credentials
- Enable IP whitelisting on Binance API keys
- **Never** enable withdrawal permissions on API keys
- Rotate API keys regularly
- Use different keys for testing and production

**Trading Safety:**
- Always start with paper trading mode
- Test thoroughly before using real money
- Set conservative position sizes
- Use stop losses on all positions
- Never share your API keys or secrets
- Monitor bot activity regularly
- Set up 2FA on your exchange account

**Infrastructure:**
- Keep Python and Node.js dependencies updated
- Run the bot on a secure server
- Use HTTPS if exposing the API
- Implement rate limiting on API endpoints
- Monitor logs for suspicious activity

### For Contributors

**Code Security:**
- Never hardcode API keys or secrets
- Validate and sanitize all user inputs
- Use parameterized queries (prevent SQL injection)
- Implement proper error handling (don't leak sensitive info)
- Follow principle of least privilege
- Review dependencies for known vulnerabilities

**Testing:**
- Test authentication and authorization
- Verify input validation
- Check for race conditions in trading logic
- Test error handling paths
- Validate risk management logic

**Pull Requests:**
- Security-sensitive PRs may require additional review
- Critical changes should be tested in paper mode first
- Document security implications in PR description

## Known Security Considerations

### API Key Storage
- API keys are stored in `.env` file (not committed to git)
- Keys are loaded as environment variables at runtime
- Never logged or exposed in error messages

### Trading Operations
- All trades require valid API authentication
- Position sizes are validated against account balance
- Risk limits are enforced before order execution
- Stop losses are mandatory on all positions

### Web Dashboard
- WebSocket connections for real-time updates
- API endpoints validate requests
- No authentication implemented (localhost only)
- **Do not expose API publicly without authentication**

### Third-Party Dependencies
- Python packages via `requirements.txt`
- Node.js packages via `package.json`
- Regular dependency audits recommended
- Known vulnerabilities patched promptly

## Security Checklist for Deployment

Before deploying to production:

- [ ] API keys stored in `.env` (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] Binance API has withdrawals disabled
- [ ] IP whitelist configured on Binance API
- [ ] 2FA enabled on exchange account
- [ ] Dashboard not exposed to public internet
- [ ] Dependencies updated to latest secure versions
- [ ] Paper mode tested thoroughly
- [ ] Stop losses configured
- [ ] Position sizes set conservatively
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery plan in place

## Common Vulnerabilities to Avoid

1. **API Key Exposure**
   - Never commit `.env` to git
   - Don't log API keys
   - Don't expose in error messages

2. **Order Manipulation**
   - Validate all order parameters
   - Check for race conditions
   - Implement position limits

3. **Financial Loss**
   - Enforce stop losses
   - Validate risk calculations
   - Test edge cases thoroughly

4. **Injection Attacks**
   - Sanitize user inputs
   - Use parameterized queries
   - Validate data types

5. **Authentication Bypass**
   - Verify API credentials before trading
   - Implement rate limiting
   - Log authentication attempts

## Incident Response Plan

If a security incident occurs:

1. **Immediate Response**
   - Stop the trading bot immediately
   - Disable API keys on exchange
   - Preserve logs for analysis
   - Assess the damage

2. **Investigation**
   - Determine root cause
   - Identify affected users/systems
   - Document the timeline

3. **Remediation**
   - Fix the vulnerability
   - Deploy the fix
   - Verify the fix works
   - Update dependencies if needed

4. **Communication**
   - Notify affected users
   - Publish security advisory
   - Update documentation
   - Create post-mortem

5. **Prevention**
   - Add tests to prevent recurrence
   - Update security guidelines
   - Review similar code paths
   - Improve monitoring

## Responsible Disclosure

We appreciate security researchers who:
- Report vulnerabilities privately first
- Allow reasonable time for a fix
- Don't exploit vulnerabilities for personal gain
- Don't access or modify user data without permission

We commit to:
- Acknowledge reports promptly
- Keep you informed of our progress
- Credit you in the fix (if you want)
- Not take legal action against good-faith researchers

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Binance API Security Best Practices](https://www.binance.com/en/support/faq/360002502072)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)

## Questions?

If you have questions about security but don't have a vulnerability to report, please open a regular GitHub issue with the "security" label.
