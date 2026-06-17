from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.slug import slugify
from db.models import Project, ProjectMembership


async def get_project_membership(
    db: AsyncSession, project_id: UUID, user_id: int
) -> ProjectMembership | None:
    stmt = select(ProjectMembership).where(
        ProjectMembership.project_id == project_id, ProjectMembership.user_id == user_id
    )
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_user_projects(db: AsyncSession, user_id: int) -> list[Project]:
    stmt = (
        select(Project)
        .join(ProjectMembership, ProjectMembership.project_id == Project.id)
        .where(ProjectMembership.user_id == user_id)
        .order_by(Project.created_at.desc())
    )

    result = await db.execute(stmt)

    return list(result.scalars().all())


async def get_user_project(
    db: AsyncSession, project_id: UUID, user_id: UUID
) -> Project | None:
    stmt = (
        select(Project)
        .join(ProjectMembership, ProjectMembership.project_id == Project.id)
        .where(
            Project.id == project_id,
            ProjectMembership.user_id == user_id,
        )
    )

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_project_with_owner(
    db: AsyncSession, name: str, slug: str, user_id: int
) -> Project:
    project = Project(name=name, slug=slug)
    db.add(project)
    await db.flush()

    membership = ProjectMembership(
        project_id=project.id,
        user_id=user_id,
        role="owner",
    )

    db.add(membership)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(project)
    return project


async def get_project_by_slug(db: AsyncSession, slug: str) -> Project | None:
    stmt = select(Project).where(Project.slug == slug)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def generate_unique_project_slug(db: AsyncSession, name: str) -> str:
    base_slug = slugify(name)
    slug = base_slug
    counter = 2

    while await get_project_by_slug(db, slug) is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
