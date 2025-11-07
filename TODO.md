# TODO.md

Project tasks and improvements for California Cannabis Market Analytics Dashboard.

---

## 🔧 High Priority: CLAUDE.md Improvements

### Missing Documentation
- [ ] Add `04-Data Quality.py` page to the Streamlit Multi-Page App Structure section
- [ ] Expand utility modules documentation with detailed descriptions of 8 key modules
- [ ] Add Filter Application Pattern section with code examples
- [ ] Add County Name Normalization section with `data_utils.py` usage
- [ ] Add Error Handling Pattern section documenting `error_messages.py` functions
- [ ] Expand Plot Helpers documentation with all available functions
- [ ] Add Environment Configuration section for `config/env.py`
- [ ] Expand Testing section with all 7 test modules and fixtures

**Files to Update:**
- `CLAUDE.md` (lines 49, 51, 74, 81, 87, 186, 188-201)

---

## 🤖 Subagent Creation

### Recommended Subagents for this Project

#### 1. Data Analyst Agent
**Priority:** High
**Purpose:** Analyze cannabis market data, sentiment trends, and business insights

```bash
claude agent create data-analyst
```

**Suggested Configuration:**
- **Description:** "Data analysis expert for cannabis market analytics. Use proactively for analyzing trends, sentiment patterns, and market insights."
- **Tools:** Read, Bash, Grep, Glob
- **Model:** sonnet
- **Use Cases:**
  - Analyze YoY growth trends
  - Identify sentiment patterns by region
  - Discover market opportunities
  - Generate business insights from data

#### 2. Streamlit Developer Agent
**Priority:** High
**Purpose:** Streamlit-specific development, debugging, and best practices

```bash
claude agent create streamlit-developer
```

**Suggested Configuration:**
- **Description:** "Streamlit application expert. Use for building pages, debugging UI issues, and optimizing dashboard performance."
- **Tools:** Read, Edit, Write, Bash, Grep, Glob
- **Model:** sonnet
- **Use Cases:**
  - Create new dashboard pages
  - Debug Streamlit caching issues
  - Optimize page load performance
  - Implement custom Streamlit components

#### 3. Test Writer Agent
**Priority:** Medium
**Purpose:** Write comprehensive pytest tests for new features

```bash
claude agent create test-writer
```

**Suggested Configuration:**
- **Description:** "Pytest testing specialist. Use proactively after implementing new features or utilities to create comprehensive tests."
- **Tools:** Read, Write, Bash, Grep, Glob
- **Model:** sonnet
- **Use Cases:**
  - Write unit tests for new utilities
  - Create fixtures for test data
  - Add integration tests for pages
  - Ensure test coverage

#### 4. Data Validator Agent
**Priority:** Medium
**Purpose:** Ensure data quality and validation

```bash
claude agent create data-validator
```

**Suggested Configuration:**
- **Description:** "Data quality specialist. Use when adding new data sources or validation rules."
- **Tools:** Read, Edit, Bash, Grep
- **Model:** sonnet
- **Use Cases:**
  - Validate CSV data integrity
  - Check for missing or malformed data
  - Implement new validation rules
  - Generate data quality reports

#### 5. Plotly Expert Agent
**Priority:** Medium
**Purpose:** Create and optimize Plotly visualizations

```bash
claude agent create plotly-expert
```

**Suggested Configuration:**
- **Description:** "Plotly visualization expert. Use for creating new charts or optimizing existing visualizations."
- **Tools:** Read, Edit, Write, Grep, Glob
- **Model:** sonnet
- **Use Cases:**
  - Create new chart types
  - Optimize chart performance
  - Apply consistent theming
  - Implement interactive features

#### 6. CSV Processor Agent
**Priority:** Low
**Purpose:** CSV data manipulation and cleaning

```bash
claude agent create csv-processor
```

**Suggested Configuration:**
- **Description:** "CSV data processing specialist. Use for data cleaning, transformation, and ETL tasks."
- **Tools:** Read, Write, Bash
- **Model:** haiku
- **Use Cases:**
  - Clean and normalize CSV data
  - Merge multiple data sources
  - Handle data transformations
  - Fix data quality issues

#### 7. Code Reviewer Agent
**Priority:** Low
**Purpose:** Python code quality review

```bash
claude agent create code-reviewer
```

**Suggested Configuration:**
- **Description:** "Python code quality reviewer. Use proactively after significant code changes."
- **Tools:** Read, Grep, Glob, Bash
- **Model:** sonnet
- **Use Cases:**
  - Review code for best practices
  - Check for security issues
  - Ensure PEP 8 compliance
  - Suggest performance improvements

---

## 🔌 MCP Server Setup

### Recommended MCP Servers

#### 1. GitHub MCP (High Priority)
**Purpose:** Version control, PR management, issue tracking

```bash
# Setup via gh CLI (if available)
# Claude Code can use the GitHub CLI automatically if installed
gh auth login
```

**Use Cases:**
- Create and manage pull requests
- Track and close issues
- Review code changes
- Manage branches

#### 2. Sentry MCP (High Priority)
**Purpose:** Error monitoring for production dashboard

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

**Use Cases:**
- Monitor production errors
- Debug user-reported issues
- Track error trends
- Set up alerts

#### 3. HuggingFace MCP (Medium Priority)
**Purpose:** Access to transformer models (project uses BERT for sentiment)

```bash
claude mcp add --transport http huggingface https://huggingface.co/mcp
```

**Use Cases:**
- Explore alternative sentiment models
- Fine-tune BERT for cannabis-specific sentiment
- Access pre-trained models
- Manage model versions

#### 4. Notion/Linear MCP (Low Priority)
**Purpose:** Project and task management

**Notion:**
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

**Linear:**
```bash
claude mcp add --transport http linear https://mcp.linear.app/mcp
```

**Use Cases:**
- Create and track tasks
- Document project decisions
- Manage sprints and milestones
- Share team knowledge

#### 5. Deployment Platform MCP (Low Priority)
**Purpose:** Deploy and manage the dashboard

**Netlify:**
```bash
claude mcp add --transport http netlify https://netlify-mcp.netlify.app/mcp
```

**Vercel:**
```bash
claude mcp add --transport http vercel https://mcp.vercel.com/
```

**Use Cases:**
- Deploy dashboard updates
- Monitor deployment status
- Manage environment variables
- View deployment logs

---

## 📊 Data & Feature Enhancements

### Data Quality Improvements
- [ ] Implement automated data validation pipeline
- [ ] Add data freshness checks
- [ ] Create data quality dashboard (enhance `04-Data Quality.py`)
- [ ] Add anomaly detection for outlier data points
- [ ] Implement data lineage tracking

### New Data Sources
- [ ] Research additional cannabis market data sources
- [ ] Add competitor analysis data
- [ ] Include regulatory change data
- [ ] Add economic indicators correlation

### New Features
- [ ] Implement export functionality (CSV, PDF reports)
- [ ] Add customizable date range selectors
- [ ] Create comparison mode (compare multiple regions/time periods)
- [ ] Add forecasting capabilities for market trends
- [ ] Implement user-defined alerts for specific metrics

---

## 🧪 Testing Improvements

### Test Coverage
- [ ] Increase test coverage to >90%
- [ ] Add integration tests for all pages
- [ ] Create end-to-end tests for critical user flows
- [ ] Add performance tests for large datasets
- [ ] Implement visual regression tests for plots

### Test Infrastructure
- [ ] Set up CI/CD pipeline with automated testing
- [ ] Add test coverage reporting
- [ ] Create test data generation utilities
- [ ] Implement mocking for external dependencies

---

## 🎨 UI/UX Enhancements

### Design Improvements
- [ ] Review and update color palette consistency
- [ ] Improve mobile responsiveness
- [ ] Add loading indicators for slow operations
- [ ] Implement better error messages for users
- [ ] Add tooltips and help text for complex metrics

### Accessibility
- [ ] Conduct accessibility audit
- [ ] Ensure WCAG 2.1 AA compliance
- [ ] Add keyboard navigation support
- [ ] Improve screen reader support
- [ ] Add high-contrast mode option

---

## 🔒 Security & Performance

### Security
- [ ] Audit dependencies for vulnerabilities (`poetry audit`)
- [ ] Implement rate limiting for API endpoints (if applicable)
- [ ] Add input sanitization for user filters
- [ ] Review and update SECURITY.md with incident response plan
- [ ] Implement security headers for deployed app

### Performance
- [ ] Profile and optimize slow data loading
- [ ] Implement lazy loading for large datasets
- [ ] Optimize Plotly chart rendering
- [ ] Add pagination for large data tables
- [ ] Implement caching strategy for expensive calculations

---

## 📝 Documentation

### User Documentation
- [ ] Create user guide for dashboard
- [ ] Add video tutorials for common tasks
- [ ] Document all available filters and metrics
- [ ] Create FAQ section
- [ ] Add troubleshooting guide

### Developer Documentation
- [ ] Expand DATA_SCHEMA.md with validation rules
- [ ] Document all utility functions with docstrings
- [ ] Create API documentation (if exposing APIs)
- [ ] Add architecture decision records (ADRs)
- [ ] Document deployment process

---

## 🚀 Deployment & DevOps

### Deployment
- [ ] Set up staging environment
- [ ] Implement blue-green deployment
- [ ] Create deployment checklist
- [ ] Add health check endpoints
- [ ] Implement graceful shutdown

### Monitoring
- [ ] Set up application monitoring (Sentry/DataDog)
- [ ] Add usage analytics
- [ ] Implement logging strategy
- [ ] Create alerting rules for critical errors
- [ ] Add performance monitoring

---

## 🔄 Code Quality

### Refactoring
- [ ] Extract repeated code into utilities
- [ ] Standardize error handling across all pages
- [ ] Consolidate duplicate validation logic
- [ ] Improve type hints throughout codebase
- [ ] Reduce cyclomatic complexity in complex functions

### Code Style
- [ ] Ensure 100% Black/isort compliance
- [ ] Address all pylint warnings
- [ ] Add pre-commit hooks for code quality
- [ ] Document complex algorithms with comments
- [ ] Standardize function naming conventions

---

## 📦 Dependency Management

### Dependencies
- [ ] Audit and update outdated packages
- [ ] Remove unused dependencies
- [ ] Pin all dependencies to specific versions
- [ ] Document why each dependency is needed
- [ ] Consider lighter alternatives for heavy packages

---

## 🌟 Future Considerations

### Machine Learning
- [ ] Fine-tune sentiment model on cannabis-specific data
- [ ] Implement market trend forecasting
- [ ] Add clustering analysis for similar counties
- [ ] Create recommendation engine for market opportunities

### Advanced Analytics
- [ ] Implement cohort analysis
- [ ] Add A/B testing framework
- [ ] Create custom metric builder
- [ ] Implement statistical significance testing

### Integrations
- [ ] Connect to real-time data sources
- [ ] Implement data warehouse integration
- [ ] Add email report scheduling
- [ ] Create Slack/Teams notifications

---

## ✅ Completed Tasks

_Tasks that have been completed will be moved here with completion date_

---

**Last Updated:** 2025-11-07
**Project:** California Cannabis Market Analytics Dashboard
**Maintainers:** Development Team
