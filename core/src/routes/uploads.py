from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from google.cloud import storage
from beanie import PydanticObjectId
from src.models.projects import Project, Version, UploadResponse
from src.config.auth import get_current_user_email
from src.config.config import settings

router = APIRouter(prefix="/projects", tags=["uploads"])

# Initialize GCS client
gcs_client = storage.Client()
bucket = gcs_client.bucket(settings.GCP_BUCKET)

@router.post("/{project_id}/upload", response_model=UploadResponse)
async def upload_tar(
    project_id: str,
    file: UploadFile = File(...),
    env_vars: str = Form(...),       # JSON string of dict
    current_path: str = Form(...),
    language: str = Form(...),
    has_dockerfile: bool = Form(False),
    owner_email: str = Depends(get_current_user_email)
):
    # Validate project
    try:
        pid = PydanticObjectId(project_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    proj = await Project.get(pid)
    if not proj or proj.owner_email != owner_email:
        raise HTTPException(status_code=404, detail="Project not found")

    # Compute next version
    count = await Version.find({"project_id": pid}).count()
    version = count + 1

    # Upload to GCS
    filename = f"{proj.name}/v{version}/{file.filename}"
    blob = bucket.blob(filename)
    content = await file.read()
    blob.upload_from_string(content)
    size = len(content)

    # Persist metadata
    metadata = Version(
        project_id=pid,
        version=version,
        filename=file.filename,
        gcs_path=filename,
        size=size,
        current_path=current_path,
        language=language,
        has_dockerfile=has_dockerfile,
        env_vars=__import__('json').loads(env_vars)
    )
    await metadata.insert()

    return UploadResponse(project_id=project_id, version=version, success=True)

@router.get("/{project_id}/download/{version}")
async def download_tar(
    project_id: str,
    version: int,
    owner_email: str = Depends(get_current_user_email)
):
    # Fetch version metadata
    try:
        pid = PydanticObjectId(project_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    ver = await Version.find_one({"project_id": pid, "version": version})
    if not ver:
        raise HTTPException(status_code=404, detail="Version not found")

    blob = bucket.blob(ver.gcs_path)
    content = blob.download_as_bytes()
    return StreamingResponse(
        iter([content]),
        media_type="application/x-tar",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_v{version}.tar"}
    )