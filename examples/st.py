from pydantic import BaseModel, field_validator


class Ticket(BaseModel):
    model_config = {'extra': 'forbid'}

    id: str
    priority: str
    description: str

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        if len(v) != 8 or not v.startswith('SUP-') or not v[4:].isdigit():
            raise ValueError('id must be in format SUP-1234')
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v not in ('low', 'medium', 'high'):
            raise ValueError('priority must be one of: low, medium, high')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip() or len(v) > 100:
            raise ValueError('description must be 1 to 100 non-empty characters')
        return v


class SupportRequest(BaseModel):
    model_config = {'extra': 'forbid'}

    ticket: Ticket
    assignee: str

    @field_validator('assignee')
    @classmethod
    def validate_assignee(cls, v):
        if v not in ('backend-team', 'frontend-team', 'security-team'):
            raise ValueError('assignee must be one of: backend-team, frontend-team, security-team')
        return v
