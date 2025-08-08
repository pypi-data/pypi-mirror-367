from elements import action 
from elements import Account


###############################################
### Rendering #################################
###############################################

# Rendering is the process of assembling a page
# in response to a request.

# This rendering function uses the chevron 
# library to add data into into webpages.


from elements.libs.utilities import slugify
class Social:
    def __init__(self, core, **kwargs):
        self.blog = {}
        self.gallery = {}
        self.authors = Account.directory()
        core.social = self
        core.state.setdefault('files', {})
        core.state['blog'] = self.blog
        core.state['gallery'] = self.gallery
        core.state['accounts'] = Account.directory()

    @property
    def posts(self):
        return sorted(self.blog.values(), key=lambda e: e.created_at, reverse=True)

    @property
    def photos(self):
        return sorted(self.gallery.values(), key=lambda e: e.created_at, reverse=True)

    @action('blog-updated')
    def blog_updated(event, core):
        if event.title:
            slug = slugify(event.title)
            event.tags.add(['d', slug])
            event._author = core.state['accounts'].get(event.pubkey)
            core.state['blog'][slug] = event

    @action('gallery-updated')
    def gallery_updated(event, core):
        if event.delete in core.state['gallery']:
            del core.state['gallery'][event.delete]
            return

        photo = core.state['files'].get(event.image)
        if photo:
            width, height = photo.dim.split('x')
            photo.width = width
            photo.height = height
            event.photo = photo

        core.state['gallery'][event.id] = event


    @action('blog-deleted')
    def blog_deleted(event, core):
        slug = event.d
        del core.state['blog'][slug]
