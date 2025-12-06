# controllers/main_controller.py
from views.home_view import HomeView
from views.new_patient_view import NewPatientView

class MainController:
    def __init__(self, stack, base=None):
        self.stack = stack
        self.base = base
        self.views = {}
        self.views["home"] = HomeView(self, base=base)
        self.views["new"] = NewPatientView(self)
        for v in self.views.values():
            self.stack.addWidget(v)

    def show_home(self, prefill: str | None = None):
        # optionally prefill search box when returning from save
        hv: HomeView = self.views["home"]
        self.stack.setCurrentWidget(hv)
        if prefill:
            hv.search_input.setText(prefill)
            hv._do_search()

    def show_new(self):
        self.stack.setCurrentWidget(self.views["new"])
