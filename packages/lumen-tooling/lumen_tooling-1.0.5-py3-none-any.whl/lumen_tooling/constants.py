"""
File: /constants.py
Created Date: Monday July 28th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Monday July 28th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from enum import Enum

class Action:
    """
    Constants for all available actions across providers and services.
    """
    # Gmail actions
    GMAIL_SEND_EMAIL = "GMAIL_SEND_EMAIL"
    GMAIL_REPLY_TO_THREAD = "GMAIL_REPLY_TO_THREAD"
    GMAIL_FETCH_MESSAGES_BY_THREAD = "GMAIL_FETCH_MESSAGES_BY_THREAD"
    GMAIL_SEND_DRAFT = "GMAIL_SEND_DRAFT"
    GMAIL_SEARCH_PEOPLE = "GMAIL_SEARCH_PEOPLE"
    GMAIL_DELETE_DRAFT = "GMAIL_DELETE_DRAFT"
    GMAIL_DELETE_MESSAGE = "GMAIL_DELETE_MESSAGE"
    GMAIL_FETCH_EMAILS = "GMAIL_FETCH_EMAILS"
    GMAIL_GET_GMAIL_ATTACHMENT = "GMAIL_GET_GMAIL_ATTACHMENT"
    GMAIL_GET_CONTACTS = "GMAIL_GET_CONTACTS"
    GMAIL_LIST_DRAFTS = "GMAIL_LIST_DRAFTS"
    GMAIL_MOVE_TO_TRASH = "GMAIL_MOVE_TO_TRASH"
    GMAIL_PATCH_LABEL = "GMAIL_PATCH_LABEL"
    GMAIL_MODIFY_EMAIL_LABELS = "GMAIL_MODIFY_EMAIL_LABELS"
    GMAIL_CREATE_LABEL = "GMAIL_CREATE_LABEL"
    GMAIL_GET_PEOPLE = "GMAIL_GET_PEOPLE"
    GMAIL_GET_PROFILE = "GMAIL_GET_PROFILE"
    GMAIL_LIST_GMAIL_LABELS = "GMAIL_LIST_GMAIL_LABELS"
    GMAIL_LIST_THREADS = "GMAIL_LIST_THREADS"
    GMAIL_MODIFY_THREAD_LABELS = "GMAIL_MODIFY_THREAD_LABELS"
    GMAIL_REMOVE_LABEL = "GMAIL_REMOVE_LABEL"

    # Calendar actions
    CALENDAR_CREATE_EVENT = "CALENDAR_CREATE_EVENT"
    CALENDAR_DELETE_EVENT = "CALENDAR_DELETE_EVENT"
    CALENDAR_LIST_EVENTS = "CALENDAR_LIST_EVENTS"
    CALENDAR_UPDATE_ACL_RULE = "CALENDAR_UPDATE_ACL_RULE"
    CALENDAR_UPDATE_CALENDAR_LIST_ENTRY = "CALENDAR_UPDATE_CALENDAR_LIST_ENTRY"
    CALENDAR_GET_EVENT_INSTANCES = "CALENDAR_GET_EVENT_INSTANCES"
    CALENDAR_CREATE_CALENDAR = "CALENDAR_CREATE_CALENDAR"
    CALENDAR_DELETE_CALENDAR = "CALENDAR_DELETE_CALENDAR"
    CALENDAR_UPDATE_CALENDAR = "CALENDAR_UPDATE_CALENDAR"
    CALENDAR_INSERT_CALENDAR_INTO_LIST = "CALENDAR_INSERT_CALENDAR_INTO_LIST"
    CALENDAR_GET_CALENDAR = "CALENDAR_GET_CALENDAR"
    CALENDAR_QUERY_FREE_BUSY = "CALENDAR_QUERY_FREE_BUSY"
    CALENDAR_PATCH_CALENDAR = "CALENDAR_PATCH_CALENDAR"
    CALENDAR_PATCH_EVENT = "CALENDAR_PATCH_EVENT"
    CALENDAR_QUICK_ADD_EVENT = "CALENDAR_QUICK_ADD_EVENT"
    CALENDAR_SYNC_EVENTS = "CALENDAR_SYNC_EVENTS"
    CALENDAR_CLEAR_CALENDAR = "CALENDAR_CLEAR_CALENDAR"
    CALENDAR_MOVE_EVENT = "CALENDAR_MOVE_EVENT"
    CALENDAR_FIND_FREE_SLOTS = "CALENDAR_FIND_FREE_SLOTS"
    CALENDAR_LIST_ACL_RULES = "CALENDAR_LIST_ACL_RULES"
    CALENDAR_LIST_GOOGLE_CALENDARS = "CALENDAR_LIST_GOOGLE_CALENDARS"
    CALENDAR_REMOVE_ATTENDEE_FROM_EVENT = "CALENDAR_REMOVE_ATTENDEE_FROM_EVENT"
    CALENDAR_LIST_SETTINGS = "CALENDAR_LIST_SETTINGS"

    
    # Drive actions
    DRIVE_CREATE_FILE = "DRIVE_CREATE_FILE"
    DRIVE_DELETE_FILE = "DRIVE_DELETE_FILE"
    DRIVE_LIST_FILES = "DRIVE_LIST_FILES"
    DRIVE_CREATE_COMMENT = "DRIVE_CREATE_COMMENT"
    DRIVE_CREATE_SHARED_DRIVE = "DRIVE_CREATE_SHARED_DRIVE"
    DRIVE_CREATE_FILE_OR_FOLDER = "DRIVE_CREATE_FILE_OR_FOLDER"
    DRIVE_CREATE_FOLDER = "DRIVE_CREATE_FOLDER"
    DRIVE_CREATE_REPLY = "DRIVE_CREATE_REPLY"
    DRIVE_CREATE_SHORTCUT = "DRIVE_CREATE_SHORTCUT"
    DRIVE_DELETE_COMMENT = "DRIVE_DELETE_COMMENT"
    DRIVE_DELETE_SHARED_DRIVE = "DRIVE_DELETE_SHARED_DRIVE"
    DRIVE_DELETE_PERMISSION = "DRIVE_DELETE_PERMISSION"
    DRIVE_DELETE_REPLY = "DRIVE_DELETE_REPLY"
    DRIVE_DOWNLOAD_FILE = "DRIVE_DOWNLOAD_FILE"
    DRIVE_EMPTY_TRASH = "DRIVE_EMPTY_TRASH"
    DRIVE_MODIFY_FILE_LABELS = "DRIVE_MODIFY_FILE_LABELS"
    DRIVE_GENERATE_FILE_IDS = "DRIVE_GENERATE_FILE_IDS"
    DRIVE_GET_ABOUT_INFORMATION = "DRIVE_GET_ABOUT_INFORMATION"
    DRIVE_GET_CHANGES_START_PAGE_TOKEN = "DRIVE_GET_CHANGES_START_PAGE_TOKEN"
    DRIVE_GET_COMMENT = "DRIVE_GET_COMMENT"
    DRIVE_GET_SHARED_DRIVE = "DRIVE_GET_SHARED_DRIVE"
    DRIVE_GET_FILE_METADATA = "DRIVE_GET_FILE_METADATA"
    DRIVE_GET_PERMISSION = "DRIVE_GET_PERMISSION"
    DRIVE_GET_REPLY = "DRIVE_GET_REPLY"
    DRIVE_GET_REVISION = "DRIVE_GET_REVISION"
    DRIVE_HIDE_SHARED_DRIVE = "DRIVE_HIDE_SHARED_DRIVE"
    DRIVE_LIST_CHANGES = "DRIVE_LIST_CHANGES"
    DRIVE_LIST_COMMENTS = "DRIVE_LIST_COMMENTS"
    DRIVE_LIST_FILES_AND_FOLDERS = "DRIVE_LIST_FILES_AND_FOLDERS"
    DRIVE_LIST_FILE_LABELS = "DRIVE_LIST_FILE_LABELS"
    DRIVE_LIST_PERMISSIONS = "DRIVE_LIST_PERMISSIONS"
    DRIVE_LIST_REPLIES = "DRIVE_LIST_REPLIES"
    DRIVE_LIST_REVISIONS = "DRIVE_LIST_REVISIONS"
    DRIVE_LIST_SHARED_DRIVES = "DRIVE_LIST_SHARED_DRIVES"
    DRIVE_MOVE_FILE = "DRIVE_MOVE_FILE"
    DRIVE_EXPORT_FILE = "DRIVE_EXPORT_FILE"
    DRIVE_UNTRASH_FILE = "DRIVE_UNTRASH_FILE"
    DRIVE_UPDATE_COMMENT = "DRIVE_UPDATE_COMMENT"
    DRIVE_UPDATE_SHARED_DRIVE = "DRIVE_UPDATE_SHARED_DRIVE"
    
    # Docs actions
    DOCS_CREATE_DOCUMENT = "DOCS_CREATE_DOCUMENT"
    DOCS_GET_DOCUMENT = "DOCS_GET_DOCUMENT"
    DOCS_CREATE_PARAGRAPH_BULLETS = "DOCS_CREATE_PARAGRAPH_BULLETS"
    DOCS_DELETE_PARAGRAPH_BULLETS = "DOCS_DELETE_PARAGRAPH_BULLETS"
    DOCS_INSERT_TABLE = "DOCS_INSERT_TABLE"
    DOCS_DELETE_TABLE = "DOCS_DELETE_TABLE"
    DOCS_INSERT_TABLE_ROW = "DOCS_INSERT_TABLE_ROW"
    DOCS_DELETE_TABLE_ROW = "DOCS_DELETE_TABLE_ROW"
    DOCS_INSERT_TABLE_COLUMN = "DOCS_INSERT_TABLE_COLUMN"
    DOCS_DELETE_TABLE_COLUMN = "DOCS_DELETE_TABLE_COLUMN"
    DOCS_CREATE_HEADER = "DOCS_CREATE_HEADER"
    DOCS_DELETE_HEADER = "DOCS_DELETE_HEADER"
    DOCS_CREATE_FOOTER = "DOCS_CREATE_FOOTER"
    DOCS_DELETE_FOOTER = "DOCS_DELETE_FOOTER"
    DOCS_CREATE_FOOTNOTE = "DOCS_CREATE_FOOTNOTE"
    DOCS_CREATE_NAMED_RANGE = "DOCS_CREATE_NAMED_RANGE"
    DOCS_DELETE_NAMED_RANGE = "DOCS_DELETE_NAMED_RANGE"
    DOCS_UPDATE_TEXT_STYLE = "DOCS_UPDATE_TEXT_STYLE"
    DOCS_UPDATE_PARAGRAPH_STYLE = "DOCS_UPDATE_PARAGRAPH_STYLE"
    DOCS_INSERT_PAGE_BREAK = "DOCS_INSERT_PAGE_BREAK"
    DOCS_INSERT_SECTION_BREAK = "DOCS_INSERT_SECTION_BREAK"
    DOCS_INSERT_INLINE_IMAGE = "DOCS_INSERT_INLINE_IMAGE"
    DOCS_REPLACE_IMAGE = "DOCS_REPLACE_IMAGE"
    DOCS_UNMERGE_TABLE_CELLS = "DOCS_UNMERGE_TABLE_CELLS"
    DOCS_UPDATE_DOCUMENT_STYLE = "DOCS_UPDATE_DOCUMENT_STYLE"
    DOCS_UPDATE_TABLE_ROW_STYLE = "DOCS_UPDATE_TABLE_ROW_STYLE"
    DOCS_COPY_DOCUMENT = "DOCS_COPY_DOCUMENT"
    DOCS_INSERT_TEXT = "DOCS_INSERT_TEXT"
    DOCS_DELETE_CONTENT_RANGE = "DOCS_DELETE_CONTENT_RANGE"
    DOCS_REPLACE_ALL_TEXT = "DOCS_REPLACE_ALL_TEXT"


ACTION_METADATA = {
    # Gmail actions
    Action.GMAIL_SEND_EMAIL: {"provider": "google", "service": "gmail", "friendly_name": "send_email"},
    Action.GMAIL_REPLY_TO_THREAD: {"provider": "google", "service": "gmail", "friendly_name": "reply_to_thread"},
    Action.GMAIL_FETCH_MESSAGES_BY_THREAD: {"provider": "google", "service": "gmail", "friendly_name": "fetch_messages_by_thread"},
    Action.GMAIL_SEND_DRAFT: {"provider": "google", "service": "gmail", "friendly_name": "send_draft"},
    Action.GMAIL_SEARCH_PEOPLE: {"provider": "google", "service": "gmail", "friendly_name": "search_people"},
    Action.GMAIL_DELETE_DRAFT: {"provider": "google", "service": "gmail", "friendly_name": "delete_draft"},
    Action.GMAIL_DELETE_MESSAGE: {"provider": "google", "service": "gmail", "friendly_name": "delete_message"},
    Action.GMAIL_FETCH_EMAILS: {"provider": "google", "service": "gmail", "friendly_name": "fetch_emails"},
    Action.GMAIL_GET_GMAIL_ATTACHMENT: {"provider": "google", "service": "gmail", "friendly_name": "get_gmail_attachment"},
    Action.GMAIL_GET_CONTACTS: {"provider": "google", "service": "gmail", "friendly_name": "get_contacts"},
    Action.GMAIL_LIST_DRAFTS: {"provider": "google", "service": "gmail", "friendly_name": "list_drafts"},
    Action.GMAIL_MOVE_TO_TRASH: {"provider": "google", "service": "gmail", "friendly_name": "move_to_trash"},
    Action.GMAIL_PATCH_LABEL: {"provider": "google", "service": "gmail", "friendly_name": "patch_label"},
    Action.GMAIL_MODIFY_EMAIL_LABELS: {"provider": "google", "service": "gmail", "friendly_name": "modify_email_labels"},
    Action.GMAIL_CREATE_LABEL: {"provider": "google", "service": "gmail", "friendly_name": "create_label"},
    Action.GMAIL_GET_PEOPLE: {"provider": "google", "service": "gmail", "friendly_name": "get_people"},
    Action.GMAIL_GET_PROFILE: {"provider": "google", "service": "gmail", "friendly_name": "get_profile"},
    Action.GMAIL_LIST_GMAIL_LABELS: {"provider": "google", "service": "gmail", "friendly_name": "list_gmail_labels"},
    Action.GMAIL_LIST_THREADS: {"provider": "google", "service": "gmail", "friendly_name": "list_threads"},
    Action.GMAIL_MODIFY_THREAD_LABELS: {"provider": "google", "service": "gmail", "friendly_name": "modify_thread_labels"},
    Action.GMAIL_REMOVE_LABEL: {"provider": "google", "service": "gmail", "friendly_name": "remove_label"},
    
    # Calendar actions
    Action.CALENDAR_CREATE_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "create_event"},
    Action.CALENDAR_DELETE_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "delete_event"},
    Action.CALENDAR_LIST_EVENTS: {"provider": "google", "service": "calendar", "friendly_name": "list_events"},
    Action.CALENDAR_UPDATE_ACL_RULE: {"provider": "google", "service": "calendar", "friendly_name": "update_acl_rule"},
    Action.CALENDAR_UPDATE_CALENDAR_LIST_ENTRY: {"provider": "google", "service": "calendar", "friendly_name": "update_calendar_list_entry"},
    Action.CALENDAR_GET_EVENT_INSTANCES: {"provider": "google", "service": "calendar", "friendly_name": "get_event_instances"},
    Action.CALENDAR_CREATE_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "create_calendar"},
    Action.CALENDAR_DELETE_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "delete_calendar"},
    Action.CALENDAR_UPDATE_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "update_calendar"},
    Action.CALENDAR_INSERT_CALENDAR_INTO_LIST: {"provider": "google", "service": "calendar", "friendly_name": "insert_calendar_into_list"},
    Action.CALENDAR_GET_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "get_calendar"},
    Action.CALENDAR_QUERY_FREE_BUSY: {"provider": "google", "service": "calendar", "friendly_name": "query_free_busy"},
    Action.CALENDAR_PATCH_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "patch_calendar"},
    Action.CALENDAR_PATCH_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "patch_event"},
    Action.CALENDAR_QUICK_ADD_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "quick_add_event"},
    Action.CALENDAR_SYNC_EVENTS: {"provider": "google", "service": "calendar", "friendly_name": "sync_events"},
    Action.CALENDAR_CLEAR_CALENDAR: {"provider": "google", "service": "calendar", "friendly_name": "clear_calendar"},
    Action.CALENDAR_MOVE_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "move_event"},
    Action.CALENDAR_FIND_FREE_SLOTS: {"provider": "google", "service": "calendar", "friendly_name": "find_free_slots"},
    Action.CALENDAR_LIST_ACL_RULES: {"provider": "google", "service": "calendar", "friendly_name": "list_acl_rules"},
    Action.CALENDAR_LIST_GOOGLE_CALENDARS: {"provider": "google", "service": "calendar", "friendly_name": "list_google_calendars"},
    Action.CALENDAR_REMOVE_ATTENDEE_FROM_EVENT: {"provider": "google", "service": "calendar", "friendly_name": "remove_attendee_from_event"},
    Action.CALENDAR_LIST_SETTINGS: {"provider": "google", "service": "calendar", "friendly_name": "list_settings"},

    # Drive actions
    Action.DRIVE_CREATE_FILE: {"provider": "google", "service": "drive", "friendly_name": "create_file"},
    Action.DRIVE_DELETE_FILE: {"provider": "google", "service": "drive", "friendly_name": "delete_file"},
    Action.DRIVE_LIST_FILES: {"provider": "google", "service": "drive", "friendly_name": "list_files"},
    Action.DRIVE_CREATE_COMMENT: {"provider": "google", "service": "drive", "friendly_name": "create_comment"},
    Action.DRIVE_CREATE_SHARED_DRIVE: {"provider": "google", "service": "drive", "friendly_name": "create_shared_drive"},
    Action.DRIVE_CREATE_FILE_OR_FOLDER: {"provider": "google", "service": "drive", "friendly_name": "create_file_or_folder"},
    Action.DRIVE_CREATE_FOLDER: {"provider": "google", "service": "drive", "friendly_name": "create_folder"},
    Action.DRIVE_CREATE_REPLY: {"provider": "google", "service": "drive", "friendly_name": "create_reply"},
    Action.DRIVE_CREATE_SHORTCUT: {"provider": "google", "service": "drive", "friendly_name": "create_shortcut"},
    Action.DRIVE_DELETE_COMMENT: {"provider": "google", "service": "drive", "friendly_name": "delete_comment"},
    Action.DRIVE_DELETE_SHARED_DRIVE: {"provider": "google", "service": "drive", "friendly_name": "delete_shared_drive"},
    Action.DRIVE_DELETE_PERMISSION: {"provider": "google", "service": "drive", "friendly_name": "delete_permission"},
    Action.DRIVE_DELETE_REPLY: {"provider": "google", "service": "drive", "friendly_name": "delete_reply"},
    Action.DRIVE_DOWNLOAD_FILE: {"provider": "google", "service": "drive", "friendly_name": "download_file"},
    Action.DRIVE_EMPTY_TRASH: {"provider": "google", "service": "drive", "friendly_name": "empty_trash"},
    Action.DRIVE_MODIFY_FILE_LABELS: {"provider": "google", "service": "drive", "friendly_name": "modify_file_labels"},
    Action.DRIVE_GENERATE_FILE_IDS: {"provider": "google", "service": "drive", "friendly_name": "generate_file_ids"},
    Action.DRIVE_GET_ABOUT_INFORMATION: {"provider": "google", "service": "drive", "friendly_name": "get_about_information"},
    Action.DRIVE_GET_CHANGES_START_PAGE_TOKEN: {"provider": "google", "service": "drive", "friendly_name": "get_changes_start_page_token"},
    Action.DRIVE_GET_COMMENT: {"provider": "google", "service": "drive", "friendly_name": "get_comment"},
    Action.DRIVE_GET_SHARED_DRIVE: {"provider": "google", "service": "drive", "friendly_name": "get_shared_drive"},
    Action.DRIVE_GET_FILE_METADATA: {"provider": "google", "service": "drive", "friendly_name": "get_file_metadata"},
    Action.DRIVE_GET_PERMISSION: {"provider": "google", "service": "drive", "friendly_name": "get_permission"},
    Action.DRIVE_GET_REPLY: {"provider": "google", "service": "drive", "friendly_name": "get_reply"},
    Action.DRIVE_GET_REVISION: {"provider": "google", "service": "drive", "friendly_name": "get_revision"},
    Action.DRIVE_HIDE_SHARED_DRIVE: {"provider": "google", "service": "drive", "friendly_name": "hide_shared_drive"},
    Action.DRIVE_LIST_CHANGES: {"provider": "google", "service": "drive", "friendly_name": "list_changes"},
    Action.DRIVE_LIST_COMMENTS: {"provider": "google", "service": "drive", "friendly_name": "list_comments"},
    Action.DRIVE_LIST_FILES_AND_FOLDERS: {"provider": "google", "service": "drive", "friendly_name": "list_files_and_folders"},
    Action.DRIVE_LIST_FILE_LABELS: {"provider": "google", "service": "drive", "friendly_name": "list_file_labels"},
    Action.DRIVE_LIST_PERMISSIONS: {"provider": "google", "service": "drive", "friendly_name": "list_permissions"},
    Action.DRIVE_LIST_REPLIES: {"provider": "google", "service": "drive", "friendly_name": "list_replies"},
    Action.DRIVE_LIST_REVISIONS: {"provider": "google", "service": "drive", "friendly_name": "list_revisions"},
    Action.DRIVE_LIST_SHARED_DRIVES: {"provider": "google", "service": "drive", "friendly_name": "list_shared_drives"},
    Action.DRIVE_MOVE_FILE: {"provider": "google", "service": "drive", "friendly_name": "move_file"},
    Action.DRIVE_EXPORT_FILE: {"provider": "google", "service": "drive", "friendly_name": "export_file"},
    Action.DRIVE_UNTRASH_FILE: {"provider": "google", "service": "drive", "friendly_name": "untrash_file"},
    Action.DRIVE_UPDATE_COMMENT: {"provider": "google", "service": "drive", "friendly_name": "update_comment"},
    Action.DRIVE_UPDATE_SHARED_DRIVE: {"provider": "google", "service": "drive", "friendly_name": "update_shared_drive"},
    
    # Docs actions
    Action.DOCS_CREATE_DOCUMENT: {"provider": "google", "service": "docs", "friendly_name": "create_document"},
    Action.DOCS_GET_DOCUMENT: {"provider": "google", "service": "docs", "friendly_name": "get_document"},
    Action.DOCS_CREATE_PARAGRAPH_BULLETS: {"provider": "google", "service": "docs", "friendly_name": "create_paragraph_bullets"},
    Action.DOCS_DELETE_PARAGRAPH_BULLETS: {"provider": "google", "service": "docs", "friendly_name": "delete_paragraph_bullets"},
    Action.DOCS_INSERT_TABLE: {"provider": "google", "service": "docs", "friendly_name": "insert_table"},
    Action.DOCS_DELETE_TABLE: {"provider": "google", "service": "docs", "friendly_name": "delete_table"},
    Action.DOCS_INSERT_TABLE_ROW: {"provider": "google", "service": "docs", "friendly_name": "insert_table_row"},
    Action.DOCS_DELETE_TABLE_ROW: {"provider": "google", "service": "docs", "friendly_name": "delete_table_row"},
    Action.DOCS_INSERT_TABLE_COLUMN: {"provider": "google", "service": "docs", "friendly_name": "insert_table_column"},
    Action.DOCS_DELETE_TABLE_COLUMN: {"provider": "google", "service": "docs", "friendly_name": "delete_table_column"},
    Action.DOCS_CREATE_HEADER: {"provider": "google", "service": "docs", "friendly_name": "create_header"},
    Action.DOCS_DELETE_HEADER: {"provider": "google", "service": "docs", "friendly_name": "delete_header"},
    Action.DOCS_CREATE_FOOTER: {"provider": "google", "service": "docs", "friendly_name": "create_footer"},
    Action.DOCS_DELETE_FOOTER: {"provider": "google", "service": "docs", "friendly_name": "delete_footer"},
    Action.DOCS_CREATE_FOOTNOTE: {"provider": "google", "service": "docs", "friendly_name": "create_footnote"},
    Action.DOCS_CREATE_NAMED_RANGE: {"provider": "google", "service": "docs", "friendly_name": "create_named_range"},
    Action.DOCS_DELETE_NAMED_RANGE: {"provider": "google", "service": "docs", "friendly_name": "delete_named_range"},
    Action.DOCS_UPDATE_TEXT_STYLE: {"provider": "google", "service": "docs", "friendly_name": "update_text_style"},
    Action.DOCS_UPDATE_PARAGRAPH_STYLE: {"provider": "google", "service": "docs", "friendly_name": "update_paragraph_style"},
    Action.DOCS_INSERT_PAGE_BREAK: {"provider": "google", "service": "docs", "friendly_name": "insert_page_break"},
    Action.DOCS_INSERT_SECTION_BREAK: {"provider": "google", "service": "docs", "friendly_name": "insert_section_break"},
    Action.DOCS_INSERT_INLINE_IMAGE: {"provider": "google", "service": "docs", "friendly_name": "insert_inline_image"},
    Action.DOCS_REPLACE_IMAGE: {"provider": "google", "service": "docs", "friendly_name": "replace_image"},
    Action.DOCS_UNMERGE_TABLE_CELLS: {"provider": "google", "service": "docs", "friendly_name": "unmerge_table_cells"},
    Action.DOCS_UPDATE_DOCUMENT_STYLE: {"provider": "google", "service": "docs", "friendly_name": "update_document_style"},
    Action.DOCS_UPDATE_TABLE_ROW_STYLE: {"provider": "google", "service": "docs", "friendly_name": "update_table_row_style"},
    Action.DOCS_COPY_DOCUMENT: {"provider": "google", "service": "docs", "friendly_name": "copy_document"},
    Action.DOCS_INSERT_TEXT: {"provider": "google", "service": "docs", "friendly_name": "insert_text"},
    Action.DOCS_DELETE_CONTENT_RANGE: {"provider": "google", "service": "docs", "friendly_name": "delete_content_range"},
    Action.DOCS_REPLACE_ALL_TEXT: {"provider": "google", "service": "docs", "friendly_name": "replace_all_text"},
}

class App:
    """
    Constants for entire app/service collections.
    """
    GMAIL = "GMAIL"
    CALENDAR = "CALENDAR"
    DRIVE = "DRIVE"
    DOCS = "DOCS"

APP_TO_ACTIONS = {
    App.GMAIL: [
        Action.GMAIL_SEND_EMAIL,
        Action.GMAIL_REPLY_TO_THREAD,
        Action.GMAIL_FETCH_MESSAGES_BY_THREAD,
        Action.GMAIL_SEND_DRAFT,
        Action.GMAIL_SEARCH_PEOPLE,
        Action.GMAIL_DELETE_DRAFT,
        Action.GMAIL_DELETE_MESSAGE,
        Action.GMAIL_FETCH_EMAILS,
        Action.GMAIL_GET_GMAIL_ATTACHMENT,
        Action.GMAIL_GET_CONTACTS,
        Action.GMAIL_LIST_DRAFTS,
        Action.GMAIL_MOVE_TO_TRASH,
        Action.GMAIL_PATCH_LABEL,
        Action.GMAIL_MODIFY_EMAIL_LABELS,
        Action.GMAIL_CREATE_LABEL,
        Action.GMAIL_GET_PEOPLE,
        Action.GMAIL_GET_PROFILE,
        Action.GMAIL_LIST_GMAIL_LABELS,
        Action.GMAIL_LIST_THREADS,
        Action.GMAIL_MODIFY_THREAD_LABELS,
        Action.GMAIL_REMOVE_LABEL,
    ],
    
    App.CALENDAR: [
        Action.CALENDAR_CREATE_EVENT,
        Action.CALENDAR_DELETE_EVENT,
        Action.CALENDAR_LIST_EVENTS,
        Action.CALENDAR_UPDATE_ACL_RULE,
        Action.CALENDAR_UPDATE_CALENDAR_LIST_ENTRY,
        Action.CALENDAR_GET_EVENT_INSTANCES,
        Action.CALENDAR_CREATE_CALENDAR,
        Action.CALENDAR_DELETE_CALENDAR,
        Action.CALENDAR_UPDATE_CALENDAR,
        Action.CALENDAR_INSERT_CALENDAR_INTO_LIST,
        Action.CALENDAR_GET_CALENDAR,
        Action.CALENDAR_QUERY_FREE_BUSY,
        Action.CALENDAR_PATCH_CALENDAR,
        Action.CALENDAR_PATCH_EVENT,
        Action.CALENDAR_QUICK_ADD_EVENT,
        Action.CALENDAR_SYNC_EVENTS,
        Action.CALENDAR_CLEAR_CALENDAR,
        Action.CALENDAR_MOVE_EVENT,
        Action.CALENDAR_FIND_FREE_SLOTS,
        Action.CALENDAR_LIST_ACL_RULES,
        Action.CALENDAR_LIST_GOOGLE_CALENDARS,
        Action.CALENDAR_REMOVE_ATTENDEE_FROM_EVENT,
        Action.CALENDAR_LIST_SETTINGS,
    ],
    
    App.DRIVE: [
        Action.DRIVE_CREATE_FILE,
        Action.DRIVE_DELETE_FILE,
        Action.DRIVE_LIST_FILES,
        Action.DRIVE_CREATE_COMMENT,
        Action.DRIVE_CREATE_SHARED_DRIVE,
        Action.DRIVE_CREATE_FILE_OR_FOLDER,
        Action.DRIVE_CREATE_FOLDER,
        Action.DRIVE_CREATE_REPLY,
        Action.DRIVE_CREATE_SHORTCUT,
        Action.DRIVE_DELETE_COMMENT,
        Action.DRIVE_DELETE_SHARED_DRIVE,
        Action.DRIVE_DELETE_PERMISSION,
        Action.DRIVE_DELETE_REPLY,
        Action.DRIVE_DOWNLOAD_FILE,
        Action.DRIVE_EMPTY_TRASH,
        Action.DRIVE_MODIFY_FILE_LABELS,
        Action.DRIVE_GENERATE_FILE_IDS,
        Action.DRIVE_GET_ABOUT_INFORMATION,
        Action.DRIVE_GET_CHANGES_START_PAGE_TOKEN,
        Action.DRIVE_GET_COMMENT,
        Action.DRIVE_GET_SHARED_DRIVE,
        Action.DRIVE_GET_FILE_METADATA,
        Action.DRIVE_GET_PERMISSION,
        Action.DRIVE_GET_REPLY,
        Action.DRIVE_GET_REVISION,
        Action.DRIVE_HIDE_SHARED_DRIVE,
        Action.DRIVE_LIST_CHANGES,
        Action.DRIVE_LIST_COMMENTS,
        Action.DRIVE_LIST_FILES_AND_FOLDERS,
        Action.DRIVE_LIST_FILE_LABELS,
        Action.DRIVE_LIST_PERMISSIONS,
        Action.DRIVE_LIST_REPLIES,
        Action.DRIVE_LIST_REVISIONS,
        Action.DRIVE_LIST_SHARED_DRIVES,
        Action.DRIVE_MOVE_FILE,
        Action.DRIVE_EXPORT_FILE,
        Action.DRIVE_UNTRASH_FILE,
        Action.DRIVE_UPDATE_COMMENT,
        Action.DRIVE_UPDATE_SHARED_DRIVE,
    ],
    
    App.DOCS: [
        Action.DOCS_CREATE_DOCUMENT,
        Action.DOCS_GET_DOCUMENT,
        Action.DOCS_CREATE_PARAGRAPH_BULLETS,
        Action.DOCS_DELETE_PARAGRAPH_BULLETS,
        Action.DOCS_INSERT_TABLE,
        Action.DOCS_DELETE_TABLE,
        Action.DOCS_INSERT_TABLE_ROW,
        Action.DOCS_DELETE_TABLE_ROW,
        Action.DOCS_INSERT_TABLE_COLUMN,
        Action.DOCS_DELETE_TABLE_COLUMN,
        Action.DOCS_CREATE_HEADER,
        Action.DOCS_DELETE_HEADER,
        Action.DOCS_CREATE_FOOTER,
        Action.DOCS_DELETE_FOOTER,
        Action.DOCS_CREATE_FOOTNOTE,
        Action.DOCS_CREATE_NAMED_RANGE,
        Action.DOCS_DELETE_NAMED_RANGE,
        Action.DOCS_UPDATE_TEXT_STYLE,
        Action.DOCS_UPDATE_PARAGRAPH_STYLE,
        Action.DOCS_INSERT_PAGE_BREAK,
        Action.DOCS_INSERT_SECTION_BREAK,
        Action.DOCS_INSERT_INLINE_IMAGE,
        Action.DOCS_REPLACE_IMAGE,
        Action.DOCS_UNMERGE_TABLE_CELLS,
        Action.DOCS_UPDATE_DOCUMENT_STYLE,
        Action.DOCS_UPDATE_TABLE_ROW_STYLE,
        Action.DOCS_COPY_DOCUMENT,
        Action.DOCS_INSERT_TEXT,
        Action.DOCS_DELETE_CONTENT_RANGE,
        Action.DOCS_REPLACE_ALL_TEXT,
    ]
}

class ServiceType(str, Enum):
    """Enumeration of supported Google services for webhook triggers."""
    GMAIL = "gmail"
    DRIVE = "drive"
    CALENDAR = "calendar"
    DOCS = "docs"

class EventType(str, Enum):
    """Enumeration of webhook event types for different services."""
    # Gmail events
    GMAIL_NEW_MESSAGE = "gmail.new_message"
    GMAIL_MESSAGE_DELETED = "gmail.message_deleted"
    GMAIL_MESSAGE_UPDATED = "gmail.message_updated"
    
    # Drive events
    DRIVE_FILE_CREATED = "drive.file_created"
    DRIVE_FILE_MODIFIED = "drive.file_modified"
    DRIVE_FILE_DELETED = "drive.file_deleted"
    DRIVE_FILE_TRASHED = "drive.file_trashed"
    DRIVE_FILE_RESTORED = "drive.file_restored"
    
    # Calendar events
    CALENDAR_EVENT_CREATED = "calendar.event_created"
    CALENDAR_EVENT_UPDATED = "calendar.event_updated"
    CALENDAR_EVENT_DELETED = "calendar.event_deleted"
    CALENDAR_SYNC = "calendar.sync"
