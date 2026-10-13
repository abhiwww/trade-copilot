import asyncio
from app.core.celery_app import celery_app
from app.core import repository as repo
from app.services.document_pipeline import DocumentAnalysisPipeline

# Instantiate the pipeline for use in the worker
pipeline = DocumentAnalysisPipeline()

@celery_app.task(name="tasks.process_document", bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """
    Durable background task to process the uploaded document.
    Moves AI pipeline (OCR, Classification, Extraction) out of the request cycle.
    """
    doc = repo.docs.get_by_id(document_id)
    if not doc:
        return {"status": "error", "message": "Document not found"}

    try:
        # 1. Read file content
        try:
            with open(doc.storage_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = "Could not read file content."

        # 2. Run AI Pipeline (Synchronous wrapper for async method)
        # Since Celery tasks are typically sync, we run the async pipeline in a loop
        loop = asyncio.get_event_loop()
        analysis = loop.run_until_complete(
            pipeline.analyze_document({
                "document_id": doc.document_id,
                "filename": doc.filename,
                "text": text,
                "size_bytes": doc.size_bytes
            })
        )

        # 3. Update Document Record
        doc.document_type = analysis.document_type
        doc.status = "Processed"
        repo.docs.save(doc.document_id, doc)

        return {"status": "success", "document_id": document_id}

    except Exception as e:
        # Log and retry if possible
        print(f"Pipeline error in background task: {e}")
        # update doc status to failed in DB
        doc.status = "Failed"
        repo.docs.save(doc.document_id, doc)

        # Retry the task after some delay if it's a transient error
        raise self.retry(exc=e, countdown=60)
