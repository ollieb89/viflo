<plan phase="3" plan="3">
  <overview>
    <phase_name>Cloud Deployment Guides</phase_name>
    <goal>Create deployment guides for major cloud platforms</goal>
  </overview>
  
  <dependencies>
    <plan>Plan 3-1: Containerization</plan>
    <plan>Plan 3-2: CI/CD Pipelines</plan>
  </dependencies>
  
  <context>
    <scope>Vercel, AWS, Railway, Render deployment</scope>
    <approach>Step-by-step guides with configurations</approach>
    <current_state>No deployment documentation exists</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create deployment skill structure</name>
      <files>.agent/skills/cloud-deployment/</files>
      <action>
Create directory:
- .agent/skills/cloud-deployment/
  - SKILL.md
  - guides/
  - configs/
  - references/
      </action>
      <verify>Directory structure complete</verify>
      <done>Structure created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Write SKILL.md</name>
      <files>.agent/skills/cloud-deployment/SKILL.md</files>
      <action>
Write SKILL.md with:
- Platform selection guide
- Deployment checklist
- Environment configuration
- Domain and SSL setup
- Monitoring basics
- Cost optimization
- Under 500 lines
      </action>
      <verify>SKILL.md comprehensive</verify>
      <done>SKILL.md written</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Vercel deployment guide</name>
      <files>.agent/skills/cloud-deployment/guides/vercel.md</files>
      <action>
Document Vercel deployment:
- Project setup
- Environment variables
- Build settings
- Custom domains
- Preview deployments
- Serverless functions
- Edge config
      </action>
      <verify>Guide covers Next.js deployment</verify>
      <done>Vercel guide complete</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create AWS deployment guide</name>
      <files>.agent/skills/cloud-deployment/guides/aws.md</files>
      <action>
Document AWS deployment patterns:
- ECS Fargate (containers)
- Lambda (serverless)
- RDS (PostgreSQL)
- S3 (static hosting)
- CloudFront (CDN)
- Route 53 (DNS)
- Cost considerations
      </action>
      <verify>Guide covers common AWS patterns</verify>
      <done>AWS guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create Railway deployment guide</name>
      <files>.agent/skills/cloud-deployment/guides/railway.md</files>
      <action>
Document Railway deployment:
- Project setup
- Database provisioning
- Environment variables
- Custom domains
- Monorepo support
- Pricing
      </action>
      <verify>Guide practical for quick deployment</verify>
      <done>Railway guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create environment configuration guide</name>
      <files>.agent/skills/cloud-deployment/references/environment-config.md</files>
      <action>
Document environment setup:
- Development vs staging vs production
- Environment variables best practices
- Feature flags
- Database per environment
- Testing in production
      </action>
      <verify>Guide helps manage multiple environments</verify>
      <done>Environment guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create domain and SSL guide</name>
      <files>.agent/skills/cloud-deployment/references/domain-ssl.md</files>
      <action>
Document domain setup:
- DNS configuration
- SSL/TLS certificates
- Custom domains on platforms
- Subdomain routing
- www vs naked domain
- Certificate renewal
      </action>
      <verify>Guide covers common domain scenarios</verify>
      <done>Domain/SSL guide complete</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md under 500 lines</check>
    <check>Vercel guide practical</check>
    <check>AWS guide covers common patterns</check>
    <check>Environment configuration documented</check>
    <check>Domain setup explained</check>
  </verification>
</plan>
