from datetime import date, timedelta, datetime

from django.contrib.auth.models import User
from django.test import Client, TestCase

from .forms.task_filter_form import TaskFilterForm
from .models import Note, Project, Task


class FormTests(TestCase):
    def test_previous_due_date(self):
        form = TaskFilterForm(
            # A 6 day interval, both ends inclusive
            {"due_date_after": "2020-01-15", "due_date_before": "2020-01-20"}
        )
        form.is_valid()
        form.previous_due_date()
        # The previous 6 day interval
        self.assertEqual(form.data["due_date_after"], "2020-01-09")
        self.assertEqual(form.data["due_date_before"], "2020-01-14")
        self.assertEqual(
            form.cleaned_data["due_date_after"], date.fromisoformat("2020-01-09")
        )
        self.assertEqual(
            form.cleaned_data["due_date_before"], date.fromisoformat("2020-01-14")
        )

    def test_previous_due_date_months(self):
        form = TaskFilterForm(
            # An interval spanning two full months
            {"due_date_after": "2020-03-01", "due_date_before": "2020-04-30"}
        )
        form.is_valid()
        form.previous_due_date()
        # The previous two months interval
        self.assertEqual(form.data["due_date_after"], "2020-01-01")
        self.assertEqual(form.data["due_date_before"], "2020-02-29")

    def test_previous_due_date_one_month(self):
        form = TaskFilterForm(
            # An interval spanning one full month
            {"due_date_after": "2020-04-01", "due_date_before": "2020-04-30"}
        )
        form.is_valid()
        form.previous_due_date()
        # The previous one month interval
        self.assertEqual(form.data["due_date_after"], "2020-03-01")
        self.assertEqual(form.data["due_date_before"], "2020-03-31")

    def test_next_due_date(self):
        form = TaskFilterForm(
            # A 6 day interval, both ends inclusive
            {"due_date_after": "2020-01-15", "due_date_before": "2020-01-20"}
        )
        form.is_valid()
        form.next_due_date()
        # The previous 6 day interval
        self.assertEqual(form.data["due_date_after"], "2020-01-21")
        self.assertEqual(form.data["due_date_before"], "2020-01-26")
        self.assertEqual(
            form.cleaned_data["due_date_after"], date.fromisoformat("2020-01-21")
        )
        self.assertEqual(
            form.cleaned_data["due_date_before"], date.fromisoformat("2020-01-26")
        )


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

    def test_tasks_only_for_members(self):
        """Ordinary users only see tasks on projects they are members"""

        user = User.objects.create_user("testuser", password="test")

        visible_project = Project(title="Visible Project")
        visible_project.save()
        visible_project.members.add(user)

        hidden_project = Project(title="Hidden Project")
        hidden_project.save()

        visible_task = Task(project=visible_project, title="Visible Task")
        visible_task.save()
        hidden_task = Task(project=hidden_project, title="Hidden Task")
        hidden_task.save()

        tasks = Task.objects.sorted_for_dashboard().visible_to_user(user).all()
        self.assertEqual(list(tasks), [visible_task])

    def test_tasks_not_yet_expired_membership(self):
        """Members see tasks on projects where their membership has not yet expired"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        tomorrow = datetime.now() + timedelta(days=1)
        project.members.add(user, through_defaults={"expires_at": tomorrow})

        task = Task(project=project, title="Test Task")
        task.save()

        tasks = Task.objects.sorted_for_dashboard().visible_to_user(user).all()
        self.assertEqual(list(tasks), [task])

    def test_tasks_expired_membership(self):
        """Members don't see tasks on projects where their membership has expired"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        yesterday = datetime.now() - timedelta(days=1)
        project.members.add(user, through_defaults={"expires_at": yesterday})

        task = Task(project=project, title="Test Task")
        task.save()

        tasks = Task.objects.sorted_for_dashboard().visible_to_user(user).all()
        self.assertEqual(list(tasks), [])

    def test_tasks_superusers_see_all(self):
        """Superusers see all tasks"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, title="Test Task")
        task.save()

        tasks = Task.objects.sorted_for_dashboard().visible_to_user(user).all()
        self.assertEqual(list(tasks), [task])


class ViewsTests(TestCase):
    def test_index_unauthenticated(self):
        """Index redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_index(self):
        """Index lists tasks"""

        User.objects.create_user("testuser", password="test", is_superuser=True)

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

    def test_index_filter(self):
        """Tasks can be filtered by project"""

        User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(project=project1, title="Test Task 1", priority=-1)
        task1.save()
        project2 = Project(title="Test Project 2")
        project2.save()
        task2 = Task(project=project2, title="Test Task 2", priority=-1)
        task2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get(f"/?project={project1.id}")
        self.assertInHTML(
            f"<option value='{project1.id}' selected>Test Project 1</option>",
            str(response.content),
        )
        self.assertContains(response, "Test Task 1")
        self.assertNotContains(response, "Test Task 2")

    def test_index_filter_form_projects(self):
        """Project filter dropdown contains projects available to the user"""

        user = User.objects.create_user("testuser", password="test")

        project1 = Project(title="Visible Project")
        project1.save()
        project1.members.add(user)

        project2 = Project(title="Hidden Project")
        project2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get(f"/?project={project1.id}")
        self.assertContains(response, "Visible Project")
        self.assertNotContains(response, "Hidden Project")

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
