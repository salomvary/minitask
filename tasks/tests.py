from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Task, Project


class ViewsTests(TestCase):
    def test_index_unauthenticated(self):
        """Index redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_index(self):
        """Index lists tasks"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "Test Project")

    def test_new_unauthenticated(self):
        """New task form redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/tasks/new")
        self.assertEqual(response.status_code, 302)

    def test_new(self):
        """New task form is rendered"""

        User.objects.create_user("testuser", password="test")

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/new")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New task")

    def test_create_unauthenticated(self):
        """Creating task redirects to login when unauthenticated"""

        client = Client()
        response = client.post("/tasks")
        self.assertEqual(response.status_code, 302)

    def test_create(self):
        """New task is created"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks", {"project": project.id, "title": "Test Task", "status": "open",}
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.all()[0]
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.project, project)

    def test_detail_unauthenticated(self):
        """Task detail redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/tasks/1")
        self.assertEqual(response.status_code, 302)

    def test_detail(self):
        """Task details are rendered"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")

    def test_edit_unauthenticated(self):
        """Task edit redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/tasks/1/edit")
        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        """Task edit form is rendered"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id) + "/edit")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")

    def test_edit_post(self):
        """Task is updated"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {"project": project.id, "title": "New Title", "status": "open",},
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(pk=task.id)
        self.assertEqual(task.title, "New Title")

    def test_edit_post_not_valid(self):
        """Task is updated"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                # "project": project.id,
                "title": "New Title"
            },
        )

        # self.assertEqual(response.status_code, 400)
        self.assertContains(response, "New Title", status_code=400)
