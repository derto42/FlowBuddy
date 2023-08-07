import test_components
module=test_components.load_addon("shortcuts")
test_components.activate_addon("shortcuts")
test_components.application.exec()