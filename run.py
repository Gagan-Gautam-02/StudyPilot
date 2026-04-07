import uvicorn
import os

if __name__ == "__main__":
    # Ensure Port strictly dynamically maps to Cloud Run's internal load balancer expectation
    port = int(os.environ.get("PORT", 8080))
    # We execute Uvicorn programmatically to completely bypass Shell syntax issues.
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
