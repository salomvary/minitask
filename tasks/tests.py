from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Task, Project, Note


class ModelTests(TestCase):
    def test_task_sort_by_status(self):
        """Tasks are sorted by status descending"""

        project = Project(title="Test Project")
        project.save()
        open_task = Task(project=project, status="open", title="open_task")
        open_task.save()
        done_task = Task(project=project, status="done", title="done_task")
        done_task.save()
        in_progress_task = Task(
            project=project, status="in_progress", title="in_progress_task"
        )
        in_progress_task.save()

        tasks = Task.objects.sorted_for_dashboard().all()
        self.assertEqual(list(tasks), [in_progress_task, open_task, done_task])

    def test_task_sort_by_due_date(self):
        """Tasks are sorted by due date ascending, nulls last"""

        project = Project(title="Test Project")
        project.save()

        task_null = Task(project=project, due_date=None, title="null")
        task_null.save()
        task_5 = Task(project=project, due_date="2020-01-05", title="5")
        task_5.save()
        task_1 = Task(project=project, due_date="2020-01-01", title="1")
        task_1.save()
        task_10 = Task(project=project, due_date="2020-01-10", title="10")
        task_10.save()

        tasks = Task.objects.sorted_for_dashboard().all()
        self.assertEqual(list(tasks), [task_1, task_5, task_10, task_null])

    def test_task_sort_by_priority(self):
        """Tasks are sorted by priority descending"""

        project = Project(title="Test Project")
        project.save()
        normal_task = Task(project=project, priority=0, title="normal")
        normal_task.save()
        high_task = Task(project=project, priority=1, title="high")
        high_task.save()
        low_task = Task(project=project, priority=-1, title="low")
        low_task.save()

        tasks = Task.objects.sorted_for_dashboard().all()
        self.assertEqual(list(tasks), [high_task, normal_task, low_task])


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
        task = Task(project=project, title="Test Task", priority=-1)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "Test Project")
        self.assertContains(response, "LOW")

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
            "/tasks",
            {
                "project": project.id,
                "title": "Test Task",
                "status": "open",
                "priority": 2,
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.all()[0]
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.project, project)
        self.assertEqual(task.priority, 2)

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
        task = Task(project=project, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "HIGHEST")

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
        task = Task(project=project, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id) + "/edit")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "highest")

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
            {
                "project": project.id,
                "title": "New Title",
                "priority": 2,
                "status": "open",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(pk=task.id)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.priority, 2)

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

    def test_create_note_unauthenticated(self):
        """Creating note redirects to login when unauthenticated"""

        client = Client()
        response = client.post("/tasks/1/note")
        self.assertEqual(response.status_code, 302)

    def test_create_note_not_found(self):
        """Creating note for a non-existent task renders 404"""

        User.objects.create_user("testuser", password="test")

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post("/tasks/1/note")

        self.assertEqual(response.status_code, 404)

    def test_create_note_not_valid(self):
        """No new note is created with invalid form data"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post("/tasks/" + str(task.id) + "/note", {"body": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Note.objects.all()), 0)

    def test_create_note(self):
        """New note is created"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/note", {"body": "Test Note"}
        )

        note = Note.objects.all()[0]
        self.assertRedirects(
            response, "/tasks/" + str(task.id) + "#note-" + str(note.id), 302
        )
        self.assertEqual(note.body, "Test Note")
        self.assertEqual(note.task, task)
        self.assertEqual(note.author, user)

    def test_edit_note_unauthenticated(self):
        """Note edit form redirects to login when unauthenticated"""

        client = Client()
        response = client.post("/notes/1/edit")
        self.assertEqual(response.status_code, 302)

    def test_edit_note(self):
        """Note edit form is rendered"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, title="Test Task")
        task.save()

        note = Note(task=task, body="Test note")
        note.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/notes/{note.id}/edit")

        self.assertContains(response, "Test note", status_code=200)

    def test_edit_note_post(self):
        """Note is updated"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, title="Test Task")
        task.save()

        note = Note(task=task, body="Test note")
        note.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(f"/notes/{note.id}/edit", {"body": "New test note"})

        self.assertRedirects(
            response, "/tasks/" + str(task.id) + "#note-" + str(note.id), 302
        )

        note = Note.objects.get(pk=note.id)
        self.assertEqual(note.body, "New test note")
