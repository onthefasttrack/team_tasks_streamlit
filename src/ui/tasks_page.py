import streamlit as st
from src.ui.task_form import render_task_form
from src.ui.task_list import (
    render_active_tasks,
    render_completed_tasks,
    render_deleted_tasks,
)
from src.ui.group_tasks import (
    render_group_active_tasks,
    render_group_completed_tasks,
    render_group_deleted_tasks,
)


def render_my_tasks_page():
    st.title('My Tasks')
    tabs = st.tabs(['Add Task', 'Active Tasks', 'Completed Tasks', 'Deleted Tasks'])
    with tabs[0]:
        render_task_form()
    with tabs[1]:
        if st.session_state.get('editing_task'):
            render_task_form(st.session_state.editing_task)
        else:
            render_active_tasks()
    with tabs[2]:
        render_completed_tasks()
    with tabs[3]:
        render_deleted_tasks()


def render_group_tasks_page():
    st.title('Group Tasks')
    tabs = st.tabs(['Active Tasks', 'Completed Tasks', 'Deleted Tasks'])
    with tabs[0]:
        render_group_active_tasks()
    with tabs[1]:
        render_group_completed_tasks()
    with tabs[2]:
        render_group_deleted_tasks()


def render_tasks_page():
    render_my_tasks_page()
