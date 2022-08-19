from app.my_test_app import views


def setup_routes(app):
    app.router.add_get("/", views.index_handler)
    app.router.add_post("/login", views.log_in)
    app.router.add_post("/logout", views.log_out)
    app.router.add_post("/create", views.create)
    app.router.add_get("/read", views.read)
    app.router.add_post("/update", views.update)
    app.router.add_post("/block", views.block)
    app.router.add_post("/unblock", views.unblock)
    app.router.add_post("/delete", views.delete)
