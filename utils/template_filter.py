def format_filesize(bytes_val):
    if not bytes_val:
        return "0 Bytes"
    for unit in ['Bytes','KB','MB','GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


def register_filters(app):
    app.jinja_env.filters['filesize'] = format_filesize