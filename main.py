import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    # handles the '/' webpage
    def get(self):
        self.render("base.html")

class NewEntry(Handler):
    # handles new-entry form submissions
    def render_entry_form(self, title="", entry="", error=""):
        self.render("new-entry.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_entry_form()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Entry(title=title, entry=entry)
            e.put()

            self.redirect("/blog/"+ str(e.key().id()))
        else:
            error = "We need both a title and entry content!"
            self.render_entry_form(title, entry, error)

class BlogEntries(Handler):
    #handles the '/blog' webpage
    def render_entries(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, entry=entry, error=error, entries=entries)
    def get(self):
        self.render_entries()

class ViewPostHandler(Handler):
    #handle viewing single post by entity id
    def render_single_entry(self, id, title="", entry="", error=""):
        single_entry = Entry.get_by_id(int(id), parent=None)
        self.render("single-entry.html", title=title, entry=entry, error=error, single_entry=single_entry)
    def get(self, id):
        if id:
            self.render_single_entry(id)
        else:
            self.render_single_entry(id, title = "nothing here!",
                        post = "there is no post with id "+ str(id))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogEntries),
    ('/new-entry', NewEntry),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
