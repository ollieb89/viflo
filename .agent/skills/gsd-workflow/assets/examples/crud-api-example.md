# Example: CRUD API Phase

This example shows a typical CRUD (Create, Read, Update, Delete) API phase.

## Phase Context

```markdown
# Phase 2 Context: Project Management API

## API Design

### Base URL
/api/v1/projects

### Authentication
Required - JWT from httpOnly cookie

### Response Format
```json
{
  "data": {},
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [{"field": "name", "message": "Required"}]
  }
}
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pagination | Offset-based | Simple, works with SQL |
| Default page size | 20 | Balance between speed and usability |
| Max page size | 100 | Prevent abuse |
| Sorting | created_at desc default | Most recent first |
| Soft delete | Yes | Data recovery |
```

## Plan 1: Database Schema

```xml
<plan phase="2" plan="1">
  <overview>
    <phase_name>Project CRUD - Database</phase_name>
    <goal>Create Project model with relationships</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 1: Authentication</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create Project model</name>
      <files>prisma/schema.prisma</files>
      <action>
Add Project model:
- id (cuid)
- name (string, max 100)
- description (text, nullable)
- status (enum: active, archived, deleted)
- owner_id (foreign key to User)
- created_at, updated_at, deleted_at (soft delete)
- Index on owner_id, status
      </action>
      <verify>npx prisma validate passes</verify>
      <done>Project model with all fields</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create ProjectMember model</name>
      <files>prisma/schema.prisma</files>
      <action>
Add ProjectMember model (many-to-many):
- id (cuid)
- project_id (foreign key)
- user_id (foreign key)
- role (enum: owner, admin, member, viewer)
- created_at
- Unique constraint on (project_id, user_id)
      </action>
      <verify>Relations correct, unique constraint defined</verify>
      <done>ProjectMember model exists</done>
    </task>
    
    <task type="manual" priority="1">
      <name>Run migration</name>
      <action>npx prisma migrate dev --name add_project_models</action>
      <verify>Migration succeeds, tables created</verify>
    </task>
  </tasks>
</plan>
```

## Plan 2: API Implementation

```xml
<plan phase="2" plan="2">
  <overview>
    <phase_name>Project CRUD - API Endpoints</phase_name>
    <goal>Implement all CRUD endpoints for projects</goal>
  </overview>
  
  <dependencies>
    <complete>Plan 1: Database Schema</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create project service layer</name>
      <files>src/services/project.ts</files>
      <action>
Create project service with functions:
- createProject(data, userId)
- getProjectById(id, userId) - check membership
- listProjects(userId, filters, pagination)
- updateProject(id, data, userId) - check ownership
- deleteProject(id, userId) - soft delete
- addProjectMember(projectId, userId, role)
- removeProjectMember(projectId, userId)
      </action>
      <verify>All functions have unit tests</verify>
      <done>Service layer complete with tests</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create POST /api/v1/projects</name>
      <files>src/app/api/v1/projects/route.ts</files>
      <action>
Create project endpoint:
- POST: Create new project
- Validate name (required, max 100)
- Set authenticated user as owner
- Create owner ProjectMember record
- Return 201 with project
- Return 401 if not authenticated
      </action>
      <verify>
curl with auth creates project, returns 201
curl without auth returns 401
      </verify>
      <done>Create endpoint works</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create GET /api/v1/projects</name>
      <files>src/app/api/v1/projects/route.ts</files>
      <action>
Create list endpoint:
- GET: List user's projects
- Support query params: page, per_page, status
- Default: page=1, per_page=20, status=active
- Return paginated results with meta
- Filter by projects where user is member
      </action>
      <verify>
Returns projects user is member of
Pagination works correctly
Filters work
      </verify>
      <done>List endpoint works</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create GET /api/v1/projects/[id]</name>
      <files>src/app/api/v1/projects/[id]/route.ts</files>
      <action>
Create get endpoint:
- GET: Get single project by ID
- Check user is member
- Return 200 with project
- Return 404 if not found
- Return 403 if not member
      </action>
      <verify>
Returns project for member
Returns 404 for non-existent
Returns 403 for non-member
      </verify>
      <done>Get endpoint works</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create PATCH /api/v1/projects/[id]</name>
      <files>src/app/api/v1/projects/[id]/route.ts</files>
      <action>
Create update endpoint:
- PATCH: Update project
- Check user has admin/owner role
- Allow updating: name, description, status
- Return 200 with updated project
- Return 403 if insufficient permissions
      </action>
      <verify>
Owner can update
Admin can update
Member cannot update
      </verify>
      <done>Update endpoint works</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create DELETE /api/v1/projects/[id]</name>
      <files>src/app/api/v1/projects/[id]/route.ts</files>
      <action>
Create delete endpoint:
- DELETE: Soft delete project
- Check user is owner
- Set status to deleted, deleted_at timestamp
- Return 204 on success
- Return 403 if not owner
      </action>
      <verify>
Owner can delete
Non-owner cannot delete
Project soft deleted (not removed from DB)
      </verify>
      <done>Delete endpoint works</done>
    </task>
  </tasks>
</plan>
```

## Plan 3: Frontend Integration

```xml
<plan phase="2" plan="3">
  <overview>
    <phase_name>Project CRUD - Frontend</phase_name>
    <goal>Create UI for project management</goal>
  </overview>
  
  <dependencies>
    <complete>Plan 2: API Implementation</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create project list page</name>
      <files>src/app/projects/page.tsx, src/components/projects/ProjectList.tsx</files>
      <action>
Create projects list:
- Fetch projects from API
- Display in card/grid layout
- Show project name, description, status
- Pagination controls
- "New Project" button
- Empty state for no projects
      </action>
      <verify>List displays correctly, pagination works</verify>
      <done>Project list page complete</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create new project modal</name>
      <files>src/components/projects/CreateProjectModal.tsx</files>
      <action>
Create project creation modal:
- Name input (required)
- Description textarea
- Submit button
- Loading state
- Error display
- Success: close modal, refresh list
      </action>
      <verify>Can create project from modal</verify>
      <done>Create modal works</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create project detail page</name>
      <files>src/app/projects/[id]/page.tsx</files>
      <action>
Create project detail page:
- Fetch single project
- Display project info
- Edit button (for owners/admins)
- Delete button (for owners)
- Members list
      </action>
      <verify>Project details display, actions work</verify>
      <done>Detail page complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create edit project modal</name>
      <files>src/components/projects/EditProjectModal.tsx</files>
      <action>
Create edit modal:
- Pre-fill with current values
- Name, description, status fields
- Save changes
- Optimistic update or refresh
      </action>
      <verify>Can edit project, changes persist</verify>
      <done>Edit modal works</done>
    </task>
  </tasks>
</plan>
```

## Verification Checklist

### API Tests
- [ ] POST /api/v1/projects creates project
- [ ] GET /api/v1/projects lists user's projects
- [ ] GET /api/v1/projects/[id] returns project
- [ ] PATCH /api/v1/projects/[id] updates project
- [ ] DELETE /api/v1/projects/[id] soft deletes
- [ ] Pagination works (page, per_page)
- [ ] Filtering works (status)
- [ ] Auth required for all endpoints
- [ ] Proper error responses

### Permission Tests
- [ ] Owner can do everything
- [ ] Admin can update, not delete
- [ ] Member can only view
- [ ] Non-member cannot access

### Frontend Tests
- [ ] List displays projects
- [ ] Can create project
- [ ] Can edit project
- [ ] Can delete project
- [ ] Pagination works
- [ ] Empty state shows
- [ ] Loading states work
- [ ] Error handling works
