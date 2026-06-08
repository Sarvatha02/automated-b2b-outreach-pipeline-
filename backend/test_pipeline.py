import asyncio
from app.services.pipeline_service import create_pipeline, run_pipeline
from app.config.store import store

async def main():
    session = create_pipeline("acme.com")
    await run_pipeline(session.id)
    print("total_companies:", session.total_companies)
    print("total_contacts:", session.total_contacts)
    print("total_emails:", session.total_emails_found)

if __name__ == "__main__":
    asyncio.run(main())
