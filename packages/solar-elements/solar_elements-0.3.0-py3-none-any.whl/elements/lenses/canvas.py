import os
import re
from elements import Event, Account, action
from elements.libs import chevron
from elements.libs.tremolo.lib.http_exceptions import Forbidden
from markdown import markdown

###############################################
### Rendering #################################
###############################################

# Rendering is the process of assembling a page
# in response to a request.

# This rendering function uses the chevron 
# library to add data into into webpages.

import hashlib

class Media(Event):

    @classmethod
    def upload(cls, part, session, **metadata):
        # part is a dict from the tremolo lib

        file_type = part.get('type', '')
        file_name = part.get('filename', '')
        file_bytes = part.get('data')

        file_path = session.account.ns('/srv') / 'uploads' / file_name
        file_path.parent.mkdir(exist_ok=True)

        ox = hashlib.sha256(file_bytes).hexdigest()

        # The hash is the original hash, usually
        x = ox

        # If it's an image, we do some processing
        if file_type.startswith('image/'):
            from io import BytesIO
            from PIL import Image


            img = Image.open(BytesIO(file_bytes))
            width, height = img.size
            metadata['dim'] = f'{width}x{height}'

            # Make a thumbnail and save it
            img.thumbnail((256,256))
            thumb_path = file_path.parent / 'thumbs' / file_name
            thumb_path = thumb_path.with_suffix('.jpeg')
            thumb_path.parent.mkdir(exist_ok=True)
            metadata['thumb'] = thumb_path.relative_to(session.account.ns('/srv'))
            img.save(thumb_path, "JPEG")

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        data = {
                **metadata,
                'url': file_path.relative_to(session.account.ns('/srv')),
                'm': file_type,
                'ox': ox,
                'x': x,
                'size': str(len(file_bytes)),
                'd': file_name
        }

        return cls('file-uploaded', **data)

class Canvas:
    # A lens for editing and rendering templates.

    # This will need to create a middleware hook
    # for accepting and saving files in POST
    # requests

    def __init__(self, core, **kwargs):
        self.core = core
        core.state.setdefault('files', {})
        core.state.setdefault('gallery', [])
        self.root = Account(kwargs.get('root', os.getcwd()))
        self.static_route = kwargs.get('static') or '/static/'
        core.add_middleware(self.canvas_middleware, 'request', priority=9)

    async def canvas_middleware(self, request, **server):
        [editing] = request.query.get('edit', [None])
        request.ctx.files = {}

        if editing:
            account = self.root

            if request.method == b"POST":
                results = await request.form()
                [file] = results.get('data')
                [name] = results.get('filename')
                with open(account.path / name, 'w') as f:
                    f.write(file)

            else:
                file_names = [p.relative_to(account.path) for p in account.path.glob('**/*.html')]
                return self.render('forms/editor.html', content=account.read(editing), file_names=file_names, filename=editing, static=self.static_route)
        if request.method == b"POST":
            session = request.ctx.get('session')
            # Session object (if existing) determines where
            # stuff gets downloaded to, along with mime type.


            if session:
                content_type = request.headers.get(b'content-type')
                print('cont', content_type)

                # Are they uploading a file?
                if content_type.startswith(b'multipart/form-data'):
                    request.params.post = {}
                    #form = await request.form()

                    #print('hmm, files?')
                    #for k in request.params.files.keys():
                    #    print('k', k, request.params.files[k][:12])

                    async for part in request.files():
                        if part.get('filename') is not None:
                            file = Media.upload(part, session=session)
                            file.sign(session)
                            await self.core.add_event(file)
                            request.ctx.files[file.x] = file
                            name = part.get('name')
                            request.params.post.setdefault(name, []).append(file.x)
                        else:
                            name = part.get('name')
                            request.params.post.setdefault(name, []).append(part.get('data').decode())

                    # TODO modify the form in-place, replacing the file name uploaded
                    # with the id of the file-uploaded event - is this needed?


                elif content_type == b'application/octet-stream':
                    with open('/save/to/image_uploaded.png', 'wb') as f:
                        # read body chunk by chunk
                          async for data in request.stream():
                              # write to file on each chunk
                              f.write(data)


    def render(self, template_name, **kwargs):
        root = self.root
    
        # We look to the "web" namespace under the subspace of
        # whichever user is running the program for the file.
        template = root.read(template_name)
    
        if template is None:
            raise ValueError
    
        # In that same folder, we use the 'components' folder 
        # to include reusable pieces of the site (e.g. comments)
        components_path = root.path / 'components'
    
        # These components can be overwritten or customized
        # by manually passing in the data as a string.
        components = kwargs.pop('components', {})
    
        # This is all of the data which gets passed to the 
        # renderer. It includes the base config, query params,
        # any submitted form data, and any keyword arguments
        # passed to the render function.
    
        # TODO: consider what data we want to pass to the canvas
        data = {
                'file_name': template_name,
                'state': self.core.state,
                **kwargs
        }
        
        # We often rely on the HTMX library to selectively
        # update page data. By default, we remove the "header"
        # and "footer" tags for all HTMX requests. This 
        # prevents us from reloading scripts, css files, etc. 
        #if "HX-Request" in request.headers:
        htmx = kwargs.get('htmx')
        if htmx:
            template = re.sub(r'{{>\s?alpha\s?}}', '', template)
            template = re.sub(r'{{>\s?omega\s?}}', '', template)
    
        # Here, we are calling a function from the chevron
        # library and then returning it.
        return chevron.render(
            template, 
            partials_dict=components,
            partials_path=components_path, 
            partials_ext="html", 
            data=data
        )

    async def static(self, filepath, response):
        path = self.root.path / filepath.decode()
        path = path.resolve()

        if any([part.startswith('.') for part in path.parts]):
            raise Forbidden('Access to hidden files is not allowed')

        if path.suffix not in mime_types:
            Forbidden(f'Access to {path.suffix} files is not allowed')

        if not str(path).startswith(str(self.root.path)):
            Forbidden(f'Path traversal is bad, mmkay?')

        if path.is_file():
            await response.sendfile(str(path), content_type=mime_types[path.suffix])

        return None

    @action('page-published')
    def page_published(event, core):
        pass

    @action('file-uploaded')
    def file_uploaded(event, core):
        core.state['files'][event.x] = event

    @action('file-deleted')
    def file_deleted(event, core):
        pass

mime_types = {
    '.aac': 'audio/aac',
    '.abw': 'application/x-abiword',
    '.apng': 'image/apng',
    '.arc': 'application/x-freearc',
    '.avif': 'image/avif',
    '.avi': 'video/x-msvideo',
    '.azw': 'application/vnd.amazon.ebook',
    '.bin': 'application/octet-stream',
    '.bmp': 'image/bmp',
    '.bz': 'application/x-bzip',
    '.bz2': 'application/x-bzip2',
    '.cda': 'application/x-cdf',
    '.csh': 'application/x-csh',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # noqa: 501
    '.eot': 'application/vnd.ms-fontobject',
    '.epub': 'application/epub+zip',

    # Note: Windows and macOS might use 'application/x-gzip'
    '.gz': 'application/gzip',

    '.gif': 'image/gif',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.ico': 'image/vnd.microsoft.icon',
    '.ics': 'text/calendar',
    '.jar': 'application/java-archive',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.js': 'text/javascript',  # Or 'application/javascript'
    '.json': 'application/json',
    '.jsonld': 'application/ld+json',
    '.mid': 'audio/midi',
    '.midi': 'audio/midi',
    '.mjs': 'text/javascript',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.mpeg': 'video/mpeg',
    '.mpkg': 'application/vnd.apple.installer+xml',
    '.odp': 'application/vnd.oasis.opendocument.presentation',
    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
    '.odt': 'application/vnd.oasis.opendocument.text',
    '.oga': 'audio/ogg',
    '.ogv': 'video/ogg',
    '.ogx': 'application/ogg',
    '.opus': 'audio/ogg',
    '.otf': 'font/otf',
    '.png': 'image/png',
    '.pdf': 'application/pdf',
    '.php': 'application/x-httpd-php',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # noqa: 501
    '.rar': 'application/vnd.rar',
    '.rtf': 'application/rtf',
    '.sh': 'application/x-sh',
    '.svg': 'image/svg+xml',
    '.tar': 'application/x-tar',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.ts': 'video/mp2t',
    '.ttf': 'font/ttf',
    '.txt': 'text/plain',
    '.vsd': 'application/vnd.visio',
    '.wav': 'audio/wav',
    '.weba': 'audio/webm',
    '.webm': 'video/webm',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.xhtml': 'application/xhtml+xml',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # noqa: 501
    '.xml': 'application/xml',  # 'text/xml' is still used sometimes
    '.xul': 'application/vnd.mozilla.xul+xml',

    # Note: Windows might use 'application/x-zip-compressed'
    '.zip': 'application/zip',

    '.3gp': 'video/3gpp',  # 'audio/3gpp' if it doesn't contain video
    '.3g2': 'video/3gpp2',  # 'audio/3gpp2' if it doesn't contain video
    '.7z': 'application/x-7z-compressed'
}
