from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class ManagementAccessMiddleware:
    """Require staff access for every management app view."""

    MANAGEMENT_MODULES = {
        "adminpanel.views",
        "video_courses.views",
        "elibrary.views",
        "testseries.views",
    }
    PUBLIC_ADMINPANEL_VIEWS = {
        "apply_coupon",
        "my_coupons",
        "use_coupon",
        "remove_coupon",
        "validate_coupon",
    }
    PUBLIC_LIVE_CLASS_VIEWS = {"live_class_join"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        module = view_func.__module__
        name = view_func.__name__
        is_management_view = module in self.MANAGEMENT_MODULES
        if module == "live_class.views" and name not in self.PUBLIC_LIVE_CLASS_VIEWS:
            is_management_view = True
        if module == "adminpanel.views" and name in self.PUBLIC_ADMINPANEL_VIEWS:
            is_management_view = False

        if is_management_view and not (
            request.user.is_authenticated and request.user.is_staff
        ):
            return redirect_to_login(request.get_full_path(), reverse("login"))
        return None
