# `main.py`

This is the **entry point** of the FastAPI application for DocMind. It initializes the app, configures CORS, mounts the frontend, and registers all backend routes.

---

##  Responsibilities

- Instantiate the FastAPI app
- Register routers from `document_routes.py` and `pipeline_routes.py`
- Mount the frontend at `/ui` using `StaticFiles`
- Enable permissive CORS (configurable in production)
- Redirect `/` to `/ui` for seamless UI access

---

## Related Files
`document_routes.py`: Handles document CRUD endpoints

`pipeline_routes.py`: Runs the full question + theme analysis pipeline

`demo/`: Frontend files served by the app

`config.py`: Referenced by routes indirectly for paths