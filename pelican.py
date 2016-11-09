import sublime
import sublime_plugin
import datetime
import os
import re
import platform
import functools


class CreateMarkdownArticleCommand(sublime_plugin.WindowCommand):
    def run(self):
        blog_path = get_setting("blog_path_%s" % platform.system(), None)
        if not get_setting("create_file_on_article", True):
            self.window.show_input_panel(
                "Post Title:", "",
                functools.partial(self.on_done, "", False),
                None, None)
        else:
            if not blog_path:
                print("Please define a blog path in your configuration file")
                return
            else:
                draft_path = os.path.join(
                    blog_path,
                    get_setting("draft_path", "drafts"))

                self.window.show_input_panel(
                    "Post Title:", "",
                    functools.partial(self.on_done, draft_path, True),
                    None, None)

    def on_done(self, path, create_file, name):
        file_data = {}
        file_data['title'] = name
        file_data['slug'] = slugify(name)
        file_data['date'] = slug_date("%Y-%m-%d")
        file_data['author'] = get_setting("author", "")

        if create_file:
            # File info
            file_name = get_setting("article_file_name",
                                    "{date}-{slug}").format(**file_data)

            file_extension = get_setting("markdown_extension", ".md")
            file_name = os.path.join(path, file_name + file_extension)

            open(file_name, 'w+', encoding='utf8', newline='').close()

            new_view = self.window.open_file(file_name)
        else:
            new_view = self.window.new_file()

        # Add basic content
        # and move the cursor to the content so we can start writing!
        def finish_creation():
            if new_view.is_loading():
                sublime.set_timeout(finish_creation, 100)
            else:
                new_view.run_command('add_basic_content', file_data)
                new_view.run_command('move_to',
                                     {"extend": "true", "to": "eof"})
        finish_creation()


class InsertBasicContent(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Post Title:", "",
                                     self.on_done, None, None)

    def on_done(self, name):
        file_data = {}
        file_data['title'] = name
        file_data['slug'] = slugify(name)
        file_data['date'] = slug_date("%Y-%m-%d")
        file_data['author'] = get_setting("author", "")
        self.window.active_view().run_command('add_basic_content', file_data)


class AddBasicContentCommand(sublime_plugin.TextCommand):
    def run(self, edit, **data):
            self.insert_content(edit, **data)

    def insert_content(self, edit, **data):
        # Let's start up our file with basic content
        content = "Title: %s\nDate: %s\n" % (
            data['title'],
            slug_date("%Y-%m-%d %H:%M:%S"))

        # (Optional) Author
        if data['author']:
            content += "Author: %s\n" % data['author']

        content += "Category: \n"\
                   "Tags: \n"\
                   "Slug: %s\n"\
                   "Status: draft"\
                   "\n\n" % data['slug']
        self.view.insert(edit, 0, content)


class UpdateDateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        date_region = self.view.find(':?date:\s*', 0, sublime.IGNORECASE)
        if not date_region:
            return

        full_date_region = sublime.Region(
            date_region.end(), self.view.line(date_region).end())
        self.view.replace(
            edit, full_date_region, slug_date("%Y-%m-%d %H:%M:%S"))

        if get_setting('show_date_on_update', True):
            full_date_region = sublime.Region(
                date_region.end(), self.view.line(date_region).end())

            self.view.show(full_date_region)


# Simple helper class
def get_setting(setting_name, default):
    settings = sublime.load_settings('Pelican.sublime-settings')

    return settings.get(setting_name, default)


def slugify(value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


def slug_date(format=None):
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, format if format else "%Y-%m-%d")
