import unittest

from addons.shortcuts.shortcuts_save import (
    GroupClass,
    TaskAlreadyInGroup,
    TaskClass,
    get_group_by_id,
    get_task_by_id,
    is_id_used,
    load_groups,
    load_tasks,
    delete_group_by_id,
    delete_task_by_id,
)


class TestGroupClass(unittest.TestCase):
    def test_group_attributes(self):
        test_group_class_1 = GroupClass("id_Test", None, None)
        test_group_class_2 = GroupClass("id_Test", "G_123456", None)

        self.assertEqual(test_group_class_1.group_id, f"G_{id(test_group_class_1)}")
        self.assertEqual(str(test_group_class_1), "id_Test")
        self.assertEqual(test_group_class_2.group_id, "G_123456")

    def test_group_task_func(self):
        test_group_class_1 = GroupClass("id_Test", None, ["T_12345", "T_987654"])
        test_group_class_2 = GroupClass("id_Test", None, ["T_12345", "T_987654"])
        test_group_class_2.remove("T_987654")

        self.assertEqual(test_group_class_2.group_tasks, ["T_12345"])

        test_group_class_2.append("T_102030")

        self.assertEqual(test_group_class_1.group_tasks, ["T_12345", "T_987654"])
        self.assertEqual(test_group_class_2.group_tasks, ["T_12345", "T_102030"])
        self.assertRaises(TaskAlreadyInGroup, test_group_class_2.append, "T_102030")

        self.assertIsInstance(test_group_class_1.create_task("Test_task", "T_908070"), TaskClass)

        self.assertIn("T_908070", test_group_class_1.group_tasks)
        test_group_class_1.delete_task("T_908070")
        self.assertNotIn("T_908070", test_group_class_1.group_tasks)


class TestTaskClass(unittest.TestCase):
    def test_task_attributes(self):
        test_task_class_1 = TaskClass(
            "attr_test",
            button_text="button test",
            url="bbc.com, http://stackoverflow.com",
            file_path=None,
            directory_path=None,
        )
        test_task_class_2 = TaskClass(
            "attr_test",
            task_id="T_123456",
            button_text="button test",
            url="bbc.com, http://stackoverflow.com",
            file_path=None,
            directory_path=None,
        )

        self.assertEqual(test_task_class_1.task_id, f"T_{id(test_task_class_1)}")
        self.assertEqual(test_task_class_2.task_id, "T_123456")

        self.assertEqual(str(test_task_class_1), "attr_test")
        self.assertIsInstance(test_task_class_1.url, list)

        self.assertEqual(test_task_class_1.url[0], "https://www.bbc.com/")
        self.assertEqual(test_task_class_1.url[1], "https://stackoverflow.com/")

        test_task_class_2.url = "github.com"
        self.assertEqual(test_task_class_2.url[0], "https://github.com/")


class TestJsonWrite(unittest.TestCase):
    def test_json_data(self):
        test_group_class_1 = GroupClass("id_Test", "G_123456", None)
        test_task_class_1 = TaskClass(
            "Json_test",
            task_id="T_102030",
            button_text="button test",
            url="bbc.com, http://stackoverflow.com",
            file_path=None,
            directory_path=None,
        )

        test_group_class_2 = get_group_by_id("G_123456")
        test_task_class_2 = get_task_by_id("T_102030")

        self.assertIsInstance(test_group_class_2, GroupClass)
        self.assertIsInstance(test_task_class_2, TaskClass)

        self.assertEqual(test_group_class_1.group_id, test_group_class_2.group_id)
        self.assertEqual(test_group_class_1.group_name, test_group_class_2.group_name)

        self.assertEqual(test_task_class_1.task_id, test_task_class_2.task_id)
        self.assertEqual(test_task_class_1.task_name, test_task_class_2.task_name)

        self.assertTrue(is_id_used("T_102030"))

        self.assertIn("G_123456", load_groups())
        self.assertIn("T_102030", load_tasks())

        delete_group_by_id("G_123456")
        delete_task_by_id("T_102030")

        self.assertNotIn("G_123456", load_groups())
        self.assertNotIn("T_102030", load_tasks())


if __name__ == "__main__":
    unittest.main()
