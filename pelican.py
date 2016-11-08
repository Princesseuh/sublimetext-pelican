import sublime
import sublime_plugin
import datetime
import os
import re
import platform, functools

class CreateMarkdownArticleCommand(sublime_plugin.WindowCommand):
    def run(self):
        blog_path = get_setting("blog_path_%s" % platform.system(), None)
        if not blog_path:
            print("Please define a blog path in your configuration file")
            return
        else:
            draft_path = os.path.join(blog_path, "drafts")
            self.window.show_input_panel("Post Title:", "", functools.partial(self.on_done, draft_path), None, None)

    def on_done(self, path, name):
        slug = slugify(name)
        date = slug_date("%Y-%m-%d")
        file_name = os.path.join(path, "%s-%s.md" % (date, slug))

        # Basic content
        content = "Title: %s\nDate: %s\n" % (name, slug_date("%Y-%m-%d %H:%M:%S"))

        # (Optional) Author
        author = get_setting("author", "")
        if author:
            content += "Author: %s\n" % author

        # To-Be-Filled content
        content += "Category: \nTags: \n"

        # Slug
        content += "Slug: %s" % slug

        content += "\n\n"

        with open(file_name, 'w+', encoding='utf8', newline='') as f:
            f.write(content)

        new_view = self.window.open_file(file_name)

# Simple helper class
def get_setting(setting_name, default):
    settings = sublime.load_settings('Pelican.sublime-settings')

    return settings.get(setting_name, default)

def slugify(value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value

def slug_date(format = None):
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, format if format else "%Y-%m-%d")