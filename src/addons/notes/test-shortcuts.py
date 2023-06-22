import tests.test_components as test_components

module = test_components.load_addon("notes")

test_components.activate_addon("notes")

test_components.application.exec()