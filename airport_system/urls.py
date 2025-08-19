from rest_framework import routers

from airport_system.views import CrewViewSet, AirportViewSet, RouteViewSet, OrderViewSet, AirplaneTypeViewSet, \
    AirplaneViewSet, FlightViewSet, TicketViewSet

app_name = "airport_system"

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = router.urls