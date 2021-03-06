from datetime import date, datetime, timedelta

from django.contrib.auth.models import Permission
from django.test import Client, TestCase, TransactionTestCase

from accounts.models import User

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

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        open_task = Task(
            project=project, created_by=user, status="open", title="open_task"
        )
        open_task.save()
        done_task = Task(
            project=project, created_by=user, status="done", title="done_task"
        )
        done_task.save()
        in_progress_task = Task(
            project=project,
            created_by=user,
            status="in_progress",
            title="in_progress_task",
        )
        in_progress_task.save()

        tasks = Task.objects.all_visible().all()
        self.assertEqual(list(tasks), [in_progress_task, open_task, done_task])

    def test_task_sort_by_due_date(self):
        """Tasks are sorted by due date ascending, nulls last"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task_null = Task(project=project, created_by=user, due_date=None, title="null")
        task_null.save()
        task_5 = Task(
            project=project, created_by=user, due_date="2020-01-05", title="5"
        )
        task_5.save()
        task_1 = Task(
            project=project, created_by=user, due_date="2020-01-01", title="1"
        )
        task_1.save()
        task_10 = Task(
            project=project, created_by=user, due_date="2020-01-10", title="10"
        )
        task_10.save()

        tasks = Task.objects.all_visible().all()
        self.assertEqual(list(tasks), [task_1, task_5, task_10, task_null])

    def test_task_sort_by_priority(self):
        """Tasks are sorted by priority descending"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        normal_task = Task(project=project, created_by=user, priority=0, title="normal")
        normal_task.save()
        high_task = Task(project=project, created_by=user, priority=1, title="high")
        high_task.save()
        low_task = Task(project=project, created_by=user, priority=-1, title="low")
        low_task.save()

        tasks = Task.objects.all_visible().all()
        self.assertEqual(list(tasks), [high_task, normal_task, low_task])

    def test_tasks_only_for_members(self):
        """Ordinary users only see tasks on projects they are members"""

        user = User.objects.create_user("testuser", password="test")

        visible_project = Project(title="Visible Project")
        visible_project.save()
        visible_project.members.add(user)

        hidden_project = Project(title="Hidden Project")
        hidden_project.save()

        visible_task = Task(
            project=visible_project, created_by=user, title="Visible Task"
        )
        visible_task.save()
        hidden_task = Task(project=hidden_project, created_by=user, title="Hidden Task")
        hidden_task.save()

        tasks = Task.objects.all_visible().visible_to_user(user).all()
        self.assertEqual(list(tasks), [visible_task])

    def test_tasks_not_yet_expired_membership(self):
        """Members see tasks on projects where their membership has not yet expired"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        tomorrow = datetime.now() + timedelta(days=1)
        project.members.add(user, through_defaults={"expires_at": tomorrow})

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        tasks = Task.objects.all_visible().visible_to_user(user).all()
        self.assertEqual(list(tasks), [task])

    def test_tasks_expired_membership(self):
        """Members don't see tasks on projects where their membership has expired"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        yesterday = datetime.now() - timedelta(days=1)
        project.members.add(user, through_defaults={"expires_at": yesterday})

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        tasks = Task.objects.all_visible().visible_to_user(user).all()
        self.assertEqual(list(tasks), [])

    def test_tasks_superusers_see_all(self):
        """Superusers see all tasks"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        tasks = Task.objects.all_visible().visible_to_user(user).all()
        self.assertEqual(list(tasks), [task])


class ViewsTests(TransactionTestCase):
    def test_index_unauthenticated(self):
        """Index redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_index(self):
        """Index lists tasks"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, created_by=user, title="Test Task", priority=-1)
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

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(
            project=project1, created_by=user, title="Test Task 1", priority=-1
        )
        task1.save()
        project2 = Project(title="Test Project 2")
        project2.save()
        task2 = Task(
            project=project2, created_by=user, title="Test Task 2", priority=-1
        )
        task2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get(f"/?project={project1.id}")
        self.assertInHTML(
            f"<option value='{project1.id}' selected>Test Project 1</option>",
            response.content.decode("utf-8"),
        )
        self.assertContains(response, "Test Task 1")
        self.assertNotContains(response, "Test Task 2")

    def test_index_no_archived_tasks(self):
        """Archived tasks are not shown"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(
            project=project1, created_by=user, title="Archived Task", is_archived=True
        )
        task1.save()
        project2 = Project(title="Test Project 2")
        project2.save()
        task2 = Task(
            project=project2, created_by=user, title="Normal Task", is_archived=False
        )
        task2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/")

        self.assertContains(response, "Normal Task")
        self.assertNotContains(response, "Archived Task")

    def test_index_no_tasks_from_archived_projects(self):
        """Tasks from archived projects are not shown"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Archived Project", is_archived=True)
        project1.save()
        task1 = Task(project=project1, created_by=user, title="Archived Project Task")
        task1.save()
        project2 = Project(title="Normal Project")
        project2.save()
        task2 = Task(project=project2, created_by=user, title="Normal Project Task")
        task2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/")

        self.assertContains(response, "Normal Project Task")
        self.assertNotContains(response, "Archived Project Task")

    def test_index_show_archived(self):
        """Archived tasks are shown when explicitly requested"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(
            project=project1, created_by=user, title="Archived Task", is_archived=True
        )
        task1.save()
        project2 = Project(title="Test Project 2")
        project2.save()
        task2 = Task(
            project=project2, created_by=user, title="Normal Task", is_archived=False
        )
        task2.save()

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/?is_archived=true")

        self.assertNotContains(response, "Normal Task")
        self.assertContains(response, "Archived Task")

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

    def test_index_filter_form_no_archived_projects(self):
        """Project filter dropdown does not contain archived projects"""

        user = User.objects.create_user("testuser", password="test")

        project1 = Project(title="Normal Project")
        project1.save()
        project1.members.add(user)

        project2 = Project(title="Archived Project", is_archived=True)
        project2.save()
        project2.members.add(user)

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get(f"/?project={project1.id}")
        self.assertContains(response, "Normal Project")
        self.assertNotContains(response, "Archived Project")

    def test_index_filter_by_tag(self):
        """Tasks can be filtered by tag"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(project=project1, created_by=user, title="Test Task 1", priority=0)
        task1.save()
        task1.tags.add("foo", "bar")
        task2 = Task(project=project1, created_by=user, title="Test Task 2", priority=0)
        task2.save()
        task2.tags.add("bar", "qux")

        client = Client()
        client.login(username="testuser", password="test")

        response = client.get("/?tags=foo")
        self.assertContains(response, "Test Task 1")
        self.assertNotContains(response, "Test Task 2")

        response = client.get("/?tags=bar,qux")
        self.assertNotContains(response, "Test Task 1")
        self.assertContains(response, "Test Task 2")

    def test_index_filter_detail_sticky(self):
        """Filter is retained when returning from the details page"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(
            project=project1, created_by=user, title="Test Task 1", priority=-1
        )
        task1.save()

        client = Client()
        client.login(username="testuser", password="test")

        # Search for something first (side effect is storing the query in the session)
        client.get(f"/?project={project1.id}")

        # Go to the detail page
        response = client.get(f"/tasks/{task1.id}")

        # TODO: a better assertion less prone to false positives
        self.assertContains(response, f"project={project1.id}", status_code=200)

    def test_index_filter_edit_sticky(self):
        """Filter is retained when returning from the edit page"""

        user = User.objects.create_user("testuser", password="test", is_superuser=True)

        project1 = Project(title="Test Project 1")
        project1.save()
        task1 = Task(
            project=project1, created_by=user, title="Test Task 1", priority=-1
        )
        task1.save()

        client = Client()
        client.login(username="testuser", password="test")

        # Search for something first (side effect is storing the query in the session)
        client.get(f"/?project={project1.id}")

        # Go to the detail page
        response = client.get(f"/tasks/{task1.id}/edit")

        # TODO: a better assertion less prone to false positives
        self.assertContains(response, f"project={project1.id}", status_code=200)

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
        self.assertInHTML("<a href='/'>Cancel</a>", response.content.decode("utf-8"))

    def test_new_assignee_required(self):
        """Default assignee is the logged in user when assignee is required"""

        with self.settings(REQUIRE_ASSIGNEE=True):
            user = User.objects.create_user("testuser", password="test")

            client = Client()
            client.login(username="testuser", password="test")
            response = client.get("/tasks/new")

            self.assertEqual(response.status_code, 200)
            self.assertInHTML(
                f"<option value={user.id} selected>testuser</option>",
                response.content.decode("utf-8"),
            )

    def test_new_back_to_referer(self):
        """New task form links back to previous page"""

        User.objects.create_user("testuser", password="test")

        client = Client()
        client.login(username="testuser", password="test")

        # Local referrer
        response = client.get(
            "/tasks/new", HTTP_REFERER="http://testserver:8000/tasks/1?foo=bar#asd"
        )
        self.assertInHTML(
            "<a href='/tasks/1?foo=bar#asd'>Cancel</a>",
            response.content.decode("utf-8"),
        )

        # External referrer
        response = client.get(
            "/tasks/new", HTTP_REFERER="http://facebook.com/tasks/1?foo=bar#asd"
        )
        self.assertInHTML("<a href='/'>Cancel</a>", response.content.decode("utf-8"))
        self.assertNotContains(response, "facebook.com")

    def test_new_visible_projects(self):
        """New task form only contains visible projects"""

        user = User.objects.create_user("testuser", password="test")

        project1 = Project(title="Visible Project")
        project1.save()
        project1.members.add(user)

        project2 = Project(title="Hidden Project")
        project2.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/new")

        self.assertContains(response, "Visible Project")
        self.assertNotContains(response, "Hidden Project")

    def test_copy(self):
        """Copy task form is rendered"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/tasks/{task.id}/copy")

        self.assertContains(response, "Test Task", status_code=200)

    def test_copy_not_found(self):
        """Copy task form is not shown if the task to copy does not exist"""

        User.objects.create_user("testuser", password="test")

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/1/copy")

        self.assertEqual(response.status_code, 404)

    def test_copy_not_member(self):
        """Copy task form is not shown if user is not member"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/tasks/{task.id}/copy")

        self.assertEqual(response.status_code, 404)

    def test_copy_visible_projects(self):
        """Copy task form only contains visible projects"""

        user = User.objects.create_user("testuser", password="test")

        project1 = Project(title="Visible Project")
        project1.save()
        project1.members.add(user)

        project2 = Project(title="Hidden Project")
        project2.save()

        task = Task(project=project1, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/tasks/{task.id}/copy")

        self.assertContains(response, "Visible Project")
        self.assertNotContains(response, "Hidden Project")

    def test_create_unauthenticated(self):
        """Creating task redirects to login when unauthenticated"""

        client = Client()
        response = client.post("/tasks")
        self.assertEqual(response.status_code, 302)

    def test_create(self):
        """New task is created"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks",
            {
                "version": 0,
                "project": project.id,
                "title": "Test Task",
                "status": "open",
                "priority": 2,
                "tags": "foo,bar",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.all()[0]
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.project, project)
        self.assertEqual(task.priority, 2)
        self.assertEqual(set(task.tags.names()), set(["foo", "bar"]))
        self.assertEqual(task.created_by, user)
        self.assertEqual(task.is_archived, False)

    def test_create_not_member(self):
        """New task is not created for a project the user is not member in"""

        User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks",
            {
                "version": 0,
                "project": project.id,
                "title": "Test Task",
                "status": "open",
                "priority": 2,
                "tags": "",
            },
        )

        self.assertEqual(response.status_code, 404)
        tasks = Task.objects.all()
        self.assertEqual(list(tasks), [])

    def test_create_due_date_required(self):
        """New task is not created if due date is required but not provided"""

        with self.settings(REQUIRE_DUE_DATE=True):

            user = User.objects.create_user("testuser", password="test")

            project = Project(title="Test Project")
            project.save()
            project.members.add(user)

            client = Client()
            client.login(username="testuser", password="test")
            response = client.post(
                "/tasks",
                {
                    "version": 0,
                    "project": project.id,
                    "title": "Test Task",
                    "status": "open",
                    "priority": 2,
                    "tags": "",
                    "due_date": "",
                },
            )

            self.assertEqual(response.status_code, 400)
            tasks = Task.objects.all()
            self.assertEqual(list(tasks), [])

    def test_create_assignee_required(self):
        """New task is not created if assignee is required but not provided"""

        with self.settings(REQUIRE_ASSIGNEE=True):

            user = User.objects.create_user("testuser", password="test")

            project = Project(title="Test Project")
            project.save()
            project.members.add(user)

            client = Client()
            client.login(username="testuser", password="test")
            response = client.post(
                "/tasks",
                {
                    "version": 0,
                    "project": project.id,
                    "title": "Test Task",
                    "status": "open",
                    "priority": 2,
                    "tags": "",
                    "assignee": "",
                },
            )

            self.assertEqual(response.status_code, 400)
            tasks = Task.objects.all()
            self.assertEqual(list(tasks), [])

    def test_create_project_not_found(self):
        """New task is not created for a project that does not exist"""

        User.objects.create_user("testuser", password="test")

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks",
            {
                "project": 1,
                "title": "Test Task",
                "status": "open",
                "priority": 2,
                "tags": "",
            },
        )

        # Should actually be 404 but anything that's not success is fine for now
        self.assertEqual(response.status_code, 400)
        tasks = Task.objects.all()
        self.assertEqual(list(tasks), [])

    def test_detail_unauthenticated(self):
        """Task detail redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/tasks/1")
        self.assertEqual(response.status_code, 302)

    def test_detail(self):
        """Task details are rendered"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="delete_task"))
        task_creator = User.objects.create_user("task.creator", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(
            project=project,
            created_by=task_creator,
            title="Test Task",
            priority=2,
            is_archived=True,
        )
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "HIGHEST")
        self.assertContains(response, "task.creator")
        self.assertContains(response, "ARCHIVED")
        # Archive button
        self.assertContains(response, 'name="is_archived"')

    def test_detail_no_delete_task_permission(self):
        """Task details has no Archive button if the user does not have delete_task permission"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task", priority=2,)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id))

        self.assertEqual(response.status_code, 200)
        # Archive button
        self.assertNotContains(response, 'name="is_archived"')

    def test_detail_not_member(self):
        """Task details are rendered"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id))

        self.assertEqual(response.status_code, 404)

    def test_edit_unauthenticated(self):
        """Task edit redirects to login when unauthenticated"""

        client = Client()
        response = client.get("/tasks/1/edit")
        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        """Task edit form is rendered"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id) + "/edit")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertContains(response, "highest")

    def test_edit_visible_projects(self):
        """Task edit form only contains projects visible to the user"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="change_task"))

        project1 = Project(title="Visible Project")
        project1.save()
        project1.members.add(user)

        project2 = Project(title="Hidden Project")
        project2.save()

        task = Task(project=project1, created_by=user, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id) + "/edit")

        self.assertContains(response, "Visible Project")
        self.assertNotContains(response, "Hidden Project")

    def test_edit_not_member(self):
        """Task edit form is not rendered if the user is not project member"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="change_task"))

        project = Project(title="Test Project")
        project.save()
        task = Task(project=project, created_by=user, title="Test Task", priority=2)
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get("/tasks/" + str(task.id) + "/edit")

        self.assertEqual(response.status_code, 404)

    def test_edit_post(self):
        """Task is updated"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="change_task"))
        task_creator = User.objects.create_user("task.creator", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(
            project=project,
            created_by=task_creator,
            title="Test Task",
            is_archived=True,
        )
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                "version": 0,
                "project": project.id,
                "title": "New Title",
                "priority": 2,
                "status": "open",
                "tags": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(pk=task.id)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.created_by, task_creator)
        self.assertEqual(task.is_archived, True)

    def test_edit_post_no_change_task_permission(self):
        """Task edit form submission is unauthorized if the user does not have change_task permission"""

        user = User.objects.create_user("testuser", password="test")
        task_creator = User.objects.create_user("task.creator", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(
            project=project,
            created_by=task_creator,
            title="Test Task",
            is_archived=True,
            version=0,
        )
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                "version": 1,
                "project": project.id,
                "title": "New Title",
                "priority": 2,
                "status": "open",
                "tags": "",
            },
        )

        # self.assertEqual(response.status_code, 401)
        task.refresh_from_db()
        self.assertEqual(task.title, "Test Task")

    def test_edit_post_no_change_task_permission_status_only(self):
        """
        Task edit form submission with status field is allowed
        even if the user does not have change_task permission
        """

        user = User.objects.create_user("testuser", password="test")
        task_creator = User.objects.create_user("task.creator", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(
            project=project,
            created_by=task_creator,
            title="Test Task",
            is_archived=True,
            status="open",
            version=0,
        )
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/edit", {"version": 0, "status": "done",},
        )

        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.status, "done")

    def test_edit_post_due_date_required(self):
        """Task is not updated if due date is required but not provided"""

        with self.settings(REQUIRE_DUE_DATE=True):

            user = User.objects.create_user("testuser", password="test")
            user.user_permissions.add(Permission.objects.get(codename="change_task"))

            project = Project(title="Test Project")
            project.save()
            project.members.add(user)

            task = Task(
                project=project,
                created_by=user,
                title="Test Task",
                is_archived=True,
                due_date=datetime.now(),
            )
            task.save()

            client = Client()
            client.login(username="testuser", password="test")
            response = client.post(
                f"/tasks/{task.id}/edit",
                {
                    "version": 0,
                    "project": project.id,
                    "title": "New Title",
                    "priority": 2,
                    "status": "open",
                    "tags": "",
                    "due_date": "",
                },
            )

            self.assertEqual(response.status_code, 400)
            task = Task.objects.get(pk=task.id)
            self.assertEqual(task.title, "Test Task")

    def test_edit_post_assignee_required(self):
        """Task is not updated if due date is required but not provided"""

        with self.settings(REQUIRE_ASSIGNEE=True):

            user = User.objects.create_user("testuser", password="test")
            user.user_permissions.add(Permission.objects.get(codename="change_task"))

            project = Project(title="Test Project")
            project.save()
            project.members.add(user)

            task = Task(
                project=project,
                created_by=user,
                title="Test Task",
                is_archived=True,
                due_date=datetime.now(),
            )
            task.save()

            client = Client()
            client.login(username="testuser", password="test")
            response = client.post(
                f"/tasks/{task.id}/edit",
                {
                    "version": 0,
                    "project": project.id,
                    "title": "New Title",
                    "priority": 2,
                    "status": "open",
                    "tags": "",
                    "assignee": "",
                },
            )

            self.assertEqual(response.status_code, 400)
            task = Task.objects.get(pk=task.id)
            self.assertEqual(task.title, "Test Task")

    def test_edit_post_not_valid(self):
        """Task is updated"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="change_task"))

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                "version": 0,
                # "project": project.id,
                "title": "New Title",
            },
        )

        # self.assertEqual(response.status_code, 400)
        self.assertContains(response, "New Title", status_code=400)

    def test_archive_post_unauthenticated(self):
        """Archiving task redirects to login when unauthenticated"""

        client = Client()
        response = client.post(
            "/tasks/1/archive", {"version": "0", "is_archived": "true"},
        )

        self.assertRedirects(response, "/accounts/login/?next=/tasks/1/archive", 302)

    def test_archive_post_not_member(self):
        """Task is not archived if the user is not project member"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="delete_task"))

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/archive",
            {"version": "0", "is_archived": "true"},
        )

        self.assertEqual(response.status_code, 404)
        task.refresh_from_db()
        self.assertEqual(task.is_archived, False)

    def test_archive_post_no_permission(self):
        """Task is not archived if the user does not have delete_task permission"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        client.post(
            "/tasks/" + str(task.id) + "/archive",
            {"version": "0", "is_archived": "true"},
        )

        # self.assertEqual(response.status_code, 404)
        task.refresh_from_db()
        self.assertEqual(task.is_archived, False)

    def test_archive_post(self):
        """Task is archived"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="delete_task"))

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        task = Task(
            project=project, created_by=user, title="Test Task", is_archived=False,
        )
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/archive",
            {"version": "0", "is_archived": "true"},
        )

        self.assertRedirects(response, "/tasks/" + str(task.id), 302)
        task.refresh_from_db()
        self.assertEqual(task.is_archived, True)

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

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        task = Task(project=project, created_by=user, title="Test Task")
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
        project.members.add(user)

        task = Task(project=project, created_by=user, title="Test Task")
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

    def test_create_note_not_member(self):
        """New note is not created if the user is not project member"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(
            "/tasks/" + str(task.id) + "/note", {"body": "Test Note"}
        )

        self.assertEqual(response.status_code, 404)
        note = Note.objects.all()
        self.assertEqual(list(note), [])

    def test_edit_note_unauthenticated(self):
        """Note edit form redirects to login when unauthenticated"""

        client = Client()
        response = client.post("/notes/1/edit")
        self.assertEqual(response.status_code, 302)

    def test_edit_note(self):
        """Note edit form is rendered"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        note = Note(task=task, body="Test note")
        note.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/notes/{note.id}/edit")

        self.assertContains(response, "Test note", status_code=200)

    def test_edit_note_not_member(self):
        """Note edit form is not rendered if the user is not project member"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        note = Note(task=task, body="Test note")
        note.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.get(f"/notes/{note.id}/edit")

        self.assertEqual(response.status_code, 404)

    def test_edit_note_post(self):
        """Note is updated"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)

        task = Task(project=project, created_by=user, title="Test Task")
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

    def test_edit_note_post_not_member(self):
        """Note is not updated if the user is not project member"""

        user = User.objects.create_user("testuser", password="test")

        project = Project(title="Test Project")
        project.save()

        task = Task(project=project, created_by=user, title="Test Task")
        task.save()

        note = Note(task=task, body="Test note")
        note.save()

        client = Client()
        client.login(username="testuser", password="test")
        response = client.post(f"/notes/{note.id}/edit", {"body": "New test note"})

        self.assertEqual(response.status_code, 404)


class ViewTestsWithTransaction(TransactionTestCase):
    """
    Some tests need to be run in real transactions but TransactionTestCase
    is significantly slower then TestCase therefore this test case should only
    contain tests that really need transactions.
    """

    # Without TransactionTestCase this test fails with the following error:
    # "An error occurred in the current transaction.
    # You can't execute queries until the end of the 'atomic' block."
    # Not entirely sure if this is a bug or feature in django.test.
    def test_edit_concurrent_post(self):
        """Concurrent edits are prevented"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="change_task"))

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task V1")
        task.save()
        task.refresh_from_db()

        client = Client()
        client.login(username="testuser", password="test")

        # First update is ok
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                "version": task.version,
                "project": project.id,
                "title": "Test Task V2",
                "priority": 0,
                "status": "open",
                "tags": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        task_updated = Task.objects.get(pk=task.id)
        self.assertEqual(task_updated.title, "Test Task V2")

        # Second update concurrently should be prevented
        response = client.post(
            "/tasks/" + str(task.id) + "/edit",
            {
                "version": task.version,
                "project": project.id,
                "title": "Test Task V3",
                "priority": 0,
                "status": "open",
            },
        )

        self.assertContains(response, "The task has been modified", status_code=409)
        updated_task = Task.objects.get(pk=task.id)
        self.assertEqual(updated_task.title, "Test Task V2")

    def test_archive_concurrent_post(self):
        """Concurrent archivals are prevented"""

        user = User.objects.create_user("testuser", password="test")
        user.user_permissions.add(Permission.objects.get(codename="delete_task"))

        project = Project(title="Test Project")
        project.save()
        project.members.add(user)
        task = Task(project=project, created_by=user, title="Test Task")
        task.save()
        task.refresh_from_db()

        client = Client()
        client.login(username="testuser", password="test")

        # First update is ok
        response = client.post(
            "/tasks/" + str(task.id) + "/archive",
            {"version": task.version, "is_archived": "true",},
        )

        self.assertEqual(response.status_code, 302)
        task_updated = Task.objects.get(pk=task.id)
        self.assertEqual(task_updated.is_archived, True)

        # Second update concurrently should be prevented
        response = client.post(
            "/tasks/" + str(task.id) + "/archive",
            {"version": task.version, "is_archived": "false",},
        )

        self.assertContains(response, "The task has been modified", status_code=409)
        updated_task = Task.objects.get(pk=task.id)
        self.assertEqual(updated_task.is_archived, True)
